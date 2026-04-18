"""
Three-stage calculation pipeline used by ``app/api/v1/calculate.py``.

Stages (CQ-08 / CI-03 refactor):

1. ``resolve_inputs(request, db)`` — validates percentages, normalizes oils
   and additives, fetches oil/additive rows from Postgres. Returns a frozen
   ``ResolvedInputs`` bundle. Raises ``HTTPException`` on invalid input or
   unknown oil IDs.

2. ``compute_recipe(inputs)`` — pure calculation. No DB, no framework. Calls
   the service-layer modules and returns a frozen ``ComputedRecipe`` bundle
   containing the API-level Pydantic models plus the raw numeric values the
   persist stage needs.

3. ``persist_calculation(user, inputs, result, db)`` — creates and commits
   the ``Calculation`` row, returns the persisted model.

The endpoint handler in ``calculate.py`` wires the three stages together and
handles HTTP concerns (status codes, response serialization, transaction
wrapping).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.additive import Additive
from app.models.calculation import Calculation
from app.models.oil import Oil
from app.models.user import User
from app.schemas.requests import AdditiveInput, CalculationRequest, LyeConfig, OilInput, WaterConfig
from app.schemas.responses import (
    AdditiveEffect,
    AdditiveOutput,
    CalculationResponse,
    FattyAcidProfile,
    LyeOutput,
    OilOutput,
    QualityMetrics,
    RecipeOutput,
    SaturatedUnsaturatedRatio,
    Warning,
)
from app.services.fatty_acid_calculator import OilFattyAcids, calculate_fatty_acid_profile
from app.services.lye_calculator import OilInput as LyeOilInput
from app.services.lye_calculator import calculate_lye, calculate_lye_with_purity
from app.services.quality_metrics_calculator import AdditiveEffect as AdditiveEffectCalc
from app.services.quality_metrics_calculator import (
    OilContribution,
    apply_additive_effects,
    calculate_base_metrics_from_oils,
)
from app.services.validation import (
    generate_superfat_warnings,
    generate_unknown_additive_warning,
    normalize_additive_inputs,
    normalize_oil_inputs,
    round_to_precision,
    validate_oil_percentages,
)
from app.services.water_calculator import (
    calculate_water_from_lye_concentration,
    calculate_water_from_lye_ratio,
    calculate_water_from_oil_percent,
)

# ---------------------------------------------------------------------------
# Stage 1 — resolved input bundle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResolvedInputs:
    """
    Validated inputs + DB lookups, ready to hand off to pure computation.

    ``unknown_additive_ids`` is carried through so the compute stage can emit
    user-facing warnings without needing a DB session.
    """

    normalized_oils: list[OilInput]
    total_oil_weight_g: float
    db_oils: dict[str, Oil]
    normalized_additives: list[AdditiveInput]
    db_additives: dict[str, Additive]
    unknown_additive_ids: list[str]
    lye: LyeConfig
    water: WaterConfig
    superfat_percent: float


async def resolve_inputs(request: CalculationRequest, db: AsyncSession) -> ResolvedInputs:
    """Validate the request, normalize oil/additive inputs, load DB rows."""
    # Step 1: Normalize oil inputs (convert between weights and percentages).
    try:
        if all(oil.weight_g is not None for oil in request.oils):
            # Weights provided — derive percentages.
            normalized_oils = normalize_oil_inputs(request.oils)
            total_oil_weight_g = sum(oil.weight_g for oil in normalized_oils)
        else:
            # Percentages provided — validate sum first, then derive weights.
            percentages = [oil.percentage for oil in request.oils if oil.percentage is not None]
            validate_oil_percentages(percentages)
            total_oil_weight_g = request.total_oil_weight_g
            normalized_oils = normalize_oil_inputs(request.oils, total_weight_g=total_oil_weight_g)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_OIL_PERCENTAGES", "message": str(exc)}},
        ) from exc

    # Step 2: Fetch oil rows from DB and reject unknown oil IDs (422).
    oil_ids = [oil.id for oil in normalized_oils]
    oil_rows = await db.execute(select(Oil).where(Oil.id.in_(oil_ids)))
    db_oils = {oil.id: oil for oil in oil_rows.scalars().all()}

    unknown_oil_ids = [oid for oid in oil_ids if oid not in db_oils]
    if unknown_oil_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "UNKNOWN_OIL_ID",
                    "message": f"Oil IDs not found in database: {', '.join(unknown_oil_ids)}",
                    "details": {"unknown_oil_ids": unknown_oil_ids},
                }
            },
        )

    # Step 3: Resolve additives (optional). Unknown IDs become warnings, not errors.
    normalized_additives: list[AdditiveInput] = []
    db_additives: dict[str, Additive] = {}
    unknown_additive_ids: list[str] = []

    if request.additives:
        normalized_additives = normalize_additive_inputs(request.additives, total_oil_weight_g)
        additive_ids = [add.id for add in normalized_additives]
        additive_rows = await db.execute(select(Additive).where(Additive.id.in_(additive_ids)))
        db_additives = {add.id: add for add in additive_rows.scalars().all()}
        unknown_additive_ids = [aid for aid in additive_ids if aid not in db_additives]

    return ResolvedInputs(
        normalized_oils=normalized_oils,
        total_oil_weight_g=total_oil_weight_g,
        db_oils=db_oils,
        normalized_additives=normalized_additives,
        db_additives=db_additives,
        unknown_additive_ids=unknown_additive_ids,
        lye=request.lye,
        water=request.water,
        superfat_percent=request.superfat_percent,
    )


# ---------------------------------------------------------------------------
# Stage 2 — pure computation bundle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ComputedRecipe:
    """
    Everything the persist and response stages need from pure computation.

    API-level (Pydantic) response pieces are carried alongside the raw scalar
    values the persisted JSONB blob still tracks (``iodine_value``,
    ``ins_value``, and the two quality-metric snapshots).
    """

    recipe: RecipeOutput
    quality_metrics: QualityMetrics
    quality_metrics_base: QualityMetrics
    additive_effects: list[AdditiveEffect]
    fatty_acid_profile: FattyAcidProfile
    saturated_unsaturated_ratio: SaturatedUnsaturatedRatio
    warnings: list[Warning]
    # Raw scalars carried for persistence.
    iodine_value: float
    ins_value: float


def compute_recipe(inputs: ResolvedInputs) -> ComputedRecipe:
    """Pure calculation — no DB, no framework. Delegates to services."""
    warnings: list[Warning] = []

    # --- Lye (pure + purity-adjusted) -----------------------------------------
    lye_inputs = [
        LyeOilInput(
            weight_g=oil.weight_g,
            sap_naoh=inputs.db_oils[oil.id].sap_value_naoh,
            sap_koh=inputs.db_oils[oil.id].sap_value_koh,
        )
        for oil in inputs.normalized_oils
    ]
    base_lye = calculate_lye(
        oils=lye_inputs,
        superfat_percent=inputs.superfat_percent,
        naoh_percent=inputs.lye.naoh_percent,
        koh_percent=inputs.lye.koh_percent,
    )
    purity_result = calculate_lye_with_purity(
        pure_koh_needed=base_lye.koh_g,
        pure_naoh_needed=base_lye.naoh_g,
        koh_purity=inputs.lye.koh_purity,
        naoh_purity=inputs.lye.naoh_purity,
    )
    for purity_warning in purity_result.warnings:
        warnings.append(
            Warning(
                code=purity_warning.type.upper(),
                message=purity_warning.message,
                severity="warning",
            )
        )

    # --- Water ------------------------------------------------------------------
    commercial_lye_total = purity_result.total_lye_g
    if inputs.water.method == "water_percent_of_oils":
        water_g = calculate_water_from_oil_percent(inputs.total_oil_weight_g, inputs.water.value)
    elif inputs.water.method == "lye_concentration":
        water_g = calculate_water_from_lye_concentration(commercial_lye_total, inputs.water.value)
    else:  # water_lye_ratio
        water_g = calculate_water_from_lye_ratio(commercial_lye_total, inputs.water.value)

    # --- Base quality metrics ---------------------------------------------------
    oil_contributions = [
        OilContribution(
            weight_g=oil.weight_g,
            percentage=oil.percentage,
            quality_contributions=inputs.db_oils[oil.id].quality_contributions,
        )
        for oil in inputs.normalized_oils
    ]
    base_metrics = calculate_base_metrics_from_oils(oil_contributions)

    # --- Additives: API response pieces + calc modifiers -----------------------
    additive_effects_list: list[AdditiveEffect] = []
    additive_calcs: list[AdditiveEffectCalc] = []
    for unknown_id in inputs.unknown_additive_ids:
        warnings.append(generate_unknown_additive_warning(unknown_id))

    for additive in inputs.normalized_additives:
        if additive.id in inputs.db_additives:
            db_add = inputs.db_additives[additive.id]
            additive_effects_list.append(
                AdditiveEffect(
                    additive_id=additive.id,
                    additive_name=db_add.common_name,
                    effects=db_add.quality_effects,
                    confidence=db_add.confidence_level,
                    verified_by_mga=db_add.verified_by_mga,
                )
            )
            additive_calcs.append(
                AdditiveEffectCalc(
                    weight_g=additive.weight_g,
                    quality_effects=db_add.quality_effects,
                    confidence_level=db_add.confidence_level,
                )
            )

    final_metrics = apply_additive_effects(base_metrics, inputs.total_oil_weight_g, additive_calcs)

    # --- Fatty acid profile + derived ratio ------------------------------------
    fatty_acid_inputs = [
        OilFattyAcids(
            percentage=oil.percentage,
            fatty_acids=inputs.db_oils[oil.id].fatty_acids,
        )
        for oil in inputs.normalized_oils
    ]
    fatty_acid_profile_calc = calculate_fatty_acid_profile(fatty_acid_inputs)
    saturated = (
        fatty_acid_profile_calc.lauric
        + fatty_acid_profile_calc.myristic
        + fatty_acid_profile_calc.palmitic
        + fatty_acid_profile_calc.stearic
    )
    unsaturated = (
        fatty_acid_profile_calc.ricinoleic
        + fatty_acid_profile_calc.oleic
        + fatty_acid_profile_calc.linoleic
        + fatty_acid_profile_calc.linolenic
    )
    sat_unsat_ratio = SaturatedUnsaturatedRatio(
        saturated=round_to_precision(saturated),
        unsaturated=round_to_precision(unsaturated),
        ratio=f"{int(saturated)}:{int(unsaturated)}",
    )

    # --- Iodine + INS (weighted average) ---------------------------------------
    iodine_value = sum(
        inputs.db_oils[oil.id].iodine_value * (oil.percentage / 100)
        for oil in inputs.normalized_oils
    )
    ins_value = sum(
        inputs.db_oils[oil.id].ins_value * (oil.percentage / 100) for oil in inputs.normalized_oils
    )

    # --- Superfat warnings ------------------------------------------------------
    warnings.extend(generate_superfat_warnings(inputs.superfat_percent))

    # --- Pydantic response assembly --------------------------------------------
    recipe = RecipeOutput(
        total_oil_weight_g=round_to_precision(inputs.total_oil_weight_g),
        oils=[
            OilOutput(
                id=oil.id,
                common_name=inputs.db_oils[oil.id].common_name,
                weight_g=round_to_precision(oil.weight_g),
                percentage=round_to_precision(oil.percentage),
            )
            for oil in inputs.normalized_oils
        ],
        lye=LyeOutput(
            naoh_weight_g=purity_result.commercial_naoh_g,
            koh_weight_g=purity_result.commercial_koh_g,
            total_lye_g=purity_result.total_lye_g,
            naoh_percent=inputs.lye.naoh_percent,
            koh_percent=inputs.lye.koh_percent,
            koh_purity=inputs.lye.koh_purity,
            naoh_purity=inputs.lye.naoh_purity,
            pure_koh_equivalent_g=purity_result.pure_koh_equivalent_g,
            pure_naoh_equivalent_g=purity_result.pure_naoh_equivalent_g,
        ),
        water_weight_g=round_to_precision(water_g),
        water_method=inputs.water.method,
        water_method_value=inputs.water.value,
        superfat_percent=inputs.superfat_percent,
        additives=[
            AdditiveOutput(
                id=add.id,
                name=(
                    inputs.db_additives[add.id].common_name
                    if add.id in inputs.db_additives
                    else add.id
                ),
                weight_g=round_to_precision(add.weight_g),
                percentage=round_to_precision(add.percentage),
            )
            for add in inputs.normalized_additives
        ]
        if inputs.normalized_additives
        else [],
    )

    iodine_rounded = round_to_precision(iodine_value)
    ins_rounded = round_to_precision(ins_value)

    quality_metrics = QualityMetrics(
        hardness=final_metrics.hardness,
        cleansing=final_metrics.cleansing,
        conditioning=final_metrics.conditioning,
        bubbly_lather=final_metrics.bubbly_lather,
        creamy_lather=final_metrics.creamy_lather,
        longevity=final_metrics.longevity,
        stability=final_metrics.stability,
        iodine=iodine_rounded,
        ins=ins_rounded,
    )
    quality_metrics_base = QualityMetrics(
        hardness=base_metrics.hardness,
        cleansing=base_metrics.cleansing,
        conditioning=base_metrics.conditioning,
        bubbly_lather=base_metrics.bubbly_lather,
        creamy_lather=base_metrics.creamy_lather,
        longevity=base_metrics.longevity,
        stability=base_metrics.stability,
        iodine=iodine_rounded,
        ins=ins_rounded,
    )
    fatty_acid_profile = FattyAcidProfile(
        lauric=fatty_acid_profile_calc.lauric,
        myristic=fatty_acid_profile_calc.myristic,
        palmitic=fatty_acid_profile_calc.palmitic,
        stearic=fatty_acid_profile_calc.stearic,
        ricinoleic=fatty_acid_profile_calc.ricinoleic,
        oleic=fatty_acid_profile_calc.oleic,
        linoleic=fatty_acid_profile_calc.linoleic,
        linolenic=fatty_acid_profile_calc.linolenic,
    )

    return ComputedRecipe(
        recipe=recipe,
        quality_metrics=quality_metrics,
        quality_metrics_base=quality_metrics_base,
        additive_effects=additive_effects_list,
        fatty_acid_profile=fatty_acid_profile,
        saturated_unsaturated_ratio=sat_unsat_ratio,
        warnings=warnings,
        iodine_value=iodine_rounded,
        ins_value=ins_rounded,
    )


# ---------------------------------------------------------------------------
# Stage 3 — persistence
# ---------------------------------------------------------------------------


def _recipe_data_payload(inputs: ResolvedInputs, computed: ComputedRecipe) -> dict[str, Any]:
    """Assemble the JSONB ``recipe_data`` snapshot."""
    return {
        "total_oil_weight_g": inputs.total_oil_weight_g,
        "oils": [
            {
                "id": oil.id,
                "common_name": inputs.db_oils[oil.id].common_name,
                "weight_g": oil.weight_g,
                "percentage": oil.percentage,
            }
            for oil in inputs.normalized_oils
        ],
        "lye": {
            "naoh_weight_g": computed.recipe.lye.naoh_weight_g,
            "koh_weight_g": computed.recipe.lye.koh_weight_g,
            "total_lye_g": computed.recipe.lye.total_lye_g,
            "naoh_percent": inputs.lye.naoh_percent,
            "koh_percent": inputs.lye.koh_percent,
            "koh_purity": inputs.lye.koh_purity,
            "naoh_purity": inputs.lye.naoh_purity,
            "pure_koh_equivalent_g": computed.recipe.lye.pure_koh_equivalent_g,
            "pure_naoh_equivalent_g": computed.recipe.lye.pure_naoh_equivalent_g,
        },
        "water_weight_g": computed.recipe.water_weight_g,
        "water_method": inputs.water.method,
        "water_method_value": inputs.water.value,
        "superfat_percent": inputs.superfat_percent,
        "additives": [
            {
                "id": add.id,
                "name": (
                    inputs.db_additives[add.id].common_name
                    if add.id in inputs.db_additives
                    else add.id
                ),
                "weight_g": add.weight_g,
                "percentage": add.percentage,
            }
            for add in inputs.normalized_additives
        ]
        if inputs.normalized_additives
        else [],
    }


def _results_data_payload(computed: ComputedRecipe) -> dict[str, Any]:
    """Assemble the JSONB ``results_data`` snapshot."""
    return {
        "quality_metrics": {
            "hardness": computed.quality_metrics.hardness,
            "cleansing": computed.quality_metrics.cleansing,
            "conditioning": computed.quality_metrics.conditioning,
            "bubbly_lather": computed.quality_metrics.bubbly_lather,
            "creamy_lather": computed.quality_metrics.creamy_lather,
            "longevity": computed.quality_metrics.longevity,
            "stability": computed.quality_metrics.stability,
            "iodine": computed.iodine_value,
            "ins": computed.ins_value,
        },
        "quality_metrics_base": {
            "hardness": computed.quality_metrics_base.hardness,
            "cleansing": computed.quality_metrics_base.cleansing,
            "conditioning": computed.quality_metrics_base.conditioning,
            "bubbly_lather": computed.quality_metrics_base.bubbly_lather,
            "creamy_lather": computed.quality_metrics_base.creamy_lather,
            "longevity": computed.quality_metrics_base.longevity,
            "stability": computed.quality_metrics_base.stability,
            "iodine": computed.iodine_value,
            "ins": computed.ins_value,
        },
        "additive_effects": [
            {
                "additive_id": effect.additive_id,
                "additive_name": effect.additive_name,
                "effects": effect.effects,
                "confidence": effect.confidence,
                "verified_by_mga": effect.verified_by_mga,
            }
            for effect in computed.additive_effects
        ],
        "fatty_acid_profile": {
            "lauric": computed.fatty_acid_profile.lauric,
            "myristic": computed.fatty_acid_profile.myristic,
            "palmitic": computed.fatty_acid_profile.palmitic,
            "stearic": computed.fatty_acid_profile.stearic,
            "ricinoleic": computed.fatty_acid_profile.ricinoleic,
            "oleic": computed.fatty_acid_profile.oleic,
            "linoleic": computed.fatty_acid_profile.linoleic,
            "linolenic": computed.fatty_acid_profile.linolenic,
        },
        "saturated_unsaturated_ratio": {
            "saturated": computed.saturated_unsaturated_ratio.saturated,
            "unsaturated": computed.saturated_unsaturated_ratio.unsaturated,
            "ratio": computed.saturated_unsaturated_ratio.ratio,
        },
    }


async def persist_calculation(
    user: User,
    inputs: ResolvedInputs,
    computed: ComputedRecipe,
    db: AsyncSession,
) -> Calculation:
    """Persist the calculation. Commits. Returns the stored row."""
    calculation_id: UUID = uuid4()
    db_calculation = Calculation(
        id=calculation_id,
        user_id=user.id,
        recipe_data=_recipe_data_payload(inputs, computed),
        results_data=_results_data_payload(computed),
    )
    db.add(db_calculation)
    await db.commit()
    return db_calculation


# ---------------------------------------------------------------------------
# Response assembly helper (used by the endpoint handler after persist).
# ---------------------------------------------------------------------------


def build_response(
    calculation_id: UUID, user_id: UUID, timestamp: datetime, computed: ComputedRecipe
) -> CalculationResponse:
    """Compose the API-level ``CalculationResponse`` from the computed bundle."""
    return CalculationResponse(
        calculation_id=calculation_id,
        timestamp=timestamp,
        user_id=user_id,
        recipe=computed.recipe,
        quality_metrics=computed.quality_metrics,
        quality_metrics_base=computed.quality_metrics_base,
        additive_effects=computed.additive_effects,
        fatty_acid_profile=computed.fatty_acid_profile,
        saturated_unsaturated_ratio=computed.saturated_unsaturated_ratio,
        warnings=computed.warnings,
    )


__all__ = [
    "ComputedRecipe",
    "ResolvedInputs",
    "build_response",
    "compute_recipe",
    "persist_calculation",
    "resolve_inputs",
]
