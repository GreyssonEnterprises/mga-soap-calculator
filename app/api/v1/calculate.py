"""
Calculation API endpoints (Tasks 3.3, 3.4, 3.5)

TDD Evidence: Tests written first in test_calculation_endpoint.py
Implements POST /api/v1/calculate and GET /api/v1/calculate/{id}
"""
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.core.security import get_current_user, validate_calculation_ownership
from app.models.user import User
from app.schemas.requests import CalculationRequest, OilInput, AdditiveInput
from app.schemas.responses import (
    CalculationResponse,
    RecipeOutput,
    OilOutput,
    LyeOutput,
    AdditiveOutput,
    QualityMetrics,
    FattyAcidProfile,
    SaturatedUnsaturatedRatio,
    AdditiveEffect,
    Warning,
    ErrorResponse,
    ErrorDetail
)
from app.models.oil import Oil
from app.models.additive import Additive
from app.models.calculation import Calculation
from app.services.lye_calculator import calculate_lye, calculate_lye_with_purity, OilInput as LyeOilInput
from app.services.water_calculator import (
    calculate_water_from_oil_percent,
    calculate_water_from_lye_concentration,
    calculate_water_from_lye_ratio
)
from app.services.quality_metrics_calculator import (
    calculate_base_metrics_from_oils,
    apply_additive_effects,
    OilContribution,
    AdditiveEffect as AdditiveEffectCalc
)
from app.services.fatty_acid_calculator import calculate_fatty_acid_profile, OilFattyAcids
from app.services.validation import (
    validate_oil_percentages,
    normalize_oil_inputs,
    normalize_additive_inputs,
    generate_superfat_warnings,
    generate_unknown_additive_warning,
    round_to_precision,
    round_quality_metrics
)

router = APIRouter(
    prefix="/api/v1",
    tags=["calculations"]
)


@router.post("/calculate", response_model=CalculationResponse, status_code=status.HTTP_200_OK)
async def create_calculation(
    request: CalculationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CalculationResponse:
    """
    Calculate soap recipe with quality metrics and additive effects.

    Per spec Section 3.1:
    - Validates oil percentages sum to 100%
    - Validates oil and additive IDs exist in database
    - Calculates lye, water, quality metrics, fatty acids
    - Applies additive effects (COMPETITIVE ADVANTAGE)
    - Generates non-blocking warnings
    - Persists calculation to database

    Args:
        request: Calculation request with oils, lye, water, superfat, additives
        db: Database session

    Returns:
        Complete calculation response with all metrics

    Raises:
        HTTPException 400: Invalid oil percentages
        HTTPException 422: Unknown oil or additive IDs
    """
    warnings: List[Warning] = []

    # Step 1: Normalize oil inputs (convert between weights and percentages)
    try:
        if all(oil.weight_g is not None for oil in request.oils):
            # Weights provided - calculate percentages
            normalized_oils = normalize_oil_inputs(request.oils)
            total_oil_weight_g = sum(oil.weight_g for oil in normalized_oils)
        else:
            # Percentages provided - need to validate sum first
            percentages = [oil.percentage for oil in request.oils if oil.percentage is not None]
            validate_oil_percentages(percentages)

            # For now, require explicit total weight for percentage-based input
            # In real implementation, this could come from user or default to 1000g
            total_oil_weight_g = 1000.0  # Default batch size
            normalized_oils = normalize_oil_inputs(request.oils, total_weight_g=total_oil_weight_g)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_OIL_PERCENTAGES",
                    "message": str(e)
                }
            }
        )

    # Step 2: Validate oil IDs exist in database and fetch data
    oil_ids = [oil.id for oil in normalized_oils]
    stmt = select(Oil).where(Oil.id.in_(oil_ids))
    result = await db.execute(stmt)
    db_oils = {oil.id: oil for oil in result.scalars().all()}

    unknown_oil_ids = [oid for oid in oil_ids if oid not in db_oils]
    if unknown_oil_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "UNKNOWN_OIL_ID",
                    "message": f"Oil IDs not found in database: {', '.join(unknown_oil_ids)}",
                    "details": {"unknown_oil_ids": unknown_oil_ids}
                }
            }
        )

    # Step 3: Calculate lye amounts
    lye_inputs = [
        LyeOilInput(
            weight_g=oil.weight_g,
            sap_naoh=db_oils[oil.id].sap_value_naoh,
            sap_koh=db_oils[oil.id].sap_value_koh
        )
        for oil in normalized_oils
    ]

    # Calculate pure lye requirements
    base_lye = calculate_lye(
        oils=lye_inputs,
        superfat_percent=request.superfat_percent,
        naoh_percent=request.lye.naoh_percent,
        koh_percent=request.lye.koh_percent
    )

    # Apply purity adjustment to get commercial weights
    purity_result = calculate_lye_with_purity(
        pure_koh_needed=base_lye.koh_g,
        pure_naoh_needed=base_lye.naoh_g,
        koh_purity=request.lye.koh_purity,
        naoh_purity=request.lye.naoh_purity
    )

    # Add purity warnings if any
    if purity_result.get('warnings'):
        for purity_warning in purity_result['warnings']:
            warnings.append(Warning(
                code=purity_warning['type'].upper(),
                message=purity_warning['message'],
                severity='warning'
            ))

    # Use commercial weights (adjusted for purity) for recipe output
    lye_result = base_lye  # Keep base for internal use if needed

    # Step 4: Calculate water amount (using commercial lye weight with purity adjustment)
    commercial_lye_total = purity_result['total_lye_g']
    if request.water.method == "water_percent_of_oils":
        water_g = calculate_water_from_oil_percent(total_oil_weight_g, request.water.value)
    elif request.water.method == "lye_concentration":
        water_g = calculate_water_from_lye_concentration(commercial_lye_total, request.water.value)
    else:  # water_lye_ratio
        water_g = calculate_water_from_lye_ratio(commercial_lye_total, request.water.value)

    # Step 5: Calculate base quality metrics from oils
    oil_contributions = [
        OilContribution(
            weight_g=oil.weight_g,
            percentage=oil.percentage,
            quality_contributions=db_oils[oil.id].quality_contributions
        )
        for oil in normalized_oils
    ]

    base_metrics = calculate_base_metrics_from_oils(oil_contributions)

    # Step 6: Handle additives and their effects
    additive_effects_list: List[AdditiveEffect] = []
    additive_calcs: List[AdditiveEffectCalc] = []

    if request.additives:
        normalized_additives = normalize_additive_inputs(request.additives, total_oil_weight_g)

        # Fetch additive data from database
        additive_ids = [add.id for add in normalized_additives]
        stmt = select(Additive).where(Additive.id.in_(additive_ids))
        result = await db.execute(stmt)
        db_additives = {add.id: add for add in result.scalars().all()}

        # Generate warnings for unknown additives
        for add_id in additive_ids:
            if add_id not in db_additives:
                warnings.append(generate_unknown_additive_warning(add_id))

        # Build additive effects list
        for additive in normalized_additives:
            if additive.id in db_additives:
                db_add = db_additives[additive.id]

                # Build response effect object
                additive_effects_list.append(AdditiveEffect(
                    additive_id=additive.id,
                    additive_name=db_add.common_name,
                    effects=db_add.quality_effects,
                    confidence=db_add.confidence_level,
                    verified_by_mga=db_add.verified_by_mga
                ))

                # Build calculation object for metric modification
                additive_calcs.append(AdditiveEffectCalc(
                    weight_g=additive.weight_g,
                    quality_effects=db_add.quality_effects,
                    confidence_level=db_add.confidence_level
                ))

    # Apply additive effects to base metrics
    final_metrics = apply_additive_effects(base_metrics, total_oil_weight_g, additive_calcs)

    # Step 7: Calculate fatty acid profile
    fatty_acid_inputs = [
        OilFattyAcids(
            percentage=oil.percentage,
            fatty_acids=db_oils[oil.id].fatty_acids
        )
        for oil in normalized_oils
    ]

    fatty_acid_profile = calculate_fatty_acid_profile(fatty_acid_inputs)

    # Calculate saturated/unsaturated ratio
    saturated = (fatty_acid_profile.lauric + fatty_acid_profile.myristic +
                 fatty_acid_profile.palmitic + fatty_acid_profile.stearic)
    unsaturated = (fatty_acid_profile.ricinoleic + fatty_acid_profile.oleic +
                   fatty_acid_profile.linoleic + fatty_acid_profile.linolenic)

    sat_unsat_ratio = SaturatedUnsaturatedRatio(
        saturated=round_to_precision(saturated),
        unsaturated=round_to_precision(unsaturated),
        ratio=f"{int(saturated)}:{int(unsaturated)}"
    )

    # Step 8: Calculate INS and Iodine values (weighted average from oils)
    iodine_value = sum(
        db_oils[oil.id].iodine_value * (oil.percentage / 100)
        for oil in normalized_oils
    )
    ins_value = sum(
        db_oils[oil.id].ins_value * (oil.percentage / 100)
        for oil in normalized_oils
    )

    # Step 9: Generate superfat warnings
    warnings.extend(generate_superfat_warnings(request.superfat_percent))

    # Step 10: Build response
    recipe_output = RecipeOutput(
        total_oil_weight_g=round_to_precision(total_oil_weight_g),
        oils=[
            OilOutput(
                id=oil.id,
                common_name=db_oils[oil.id].common_name,  # Fixed: was 'name', spec requires 'common_name'
                weight_g=round_to_precision(oil.weight_g),
                percentage=round_to_precision(oil.percentage)
            )
            for oil in normalized_oils
        ],
        lye=LyeOutput(
            naoh_weight_g=purity_result['commercial_naoh_g'],  # Commercial weight (purity-adjusted)
            koh_weight_g=purity_result['commercial_koh_g'],    # Commercial weight (purity-adjusted)
            total_lye_g=purity_result['total_lye_g'],
            naoh_percent=request.lye.naoh_percent,
            koh_percent=request.lye.koh_percent,
            koh_purity=request.lye.koh_purity,
            naoh_purity=request.lye.naoh_purity,
            pure_koh_equivalent_g=purity_result['pure_koh_equivalent_g'],
            pure_naoh_equivalent_g=purity_result['pure_naoh_equivalent_g']
        ),
        water_weight_g=round_to_precision(water_g),
        water_method=request.water.method,  # Fixed: Added missing field
        water_method_value=request.water.value,  # Fixed: Added missing field
        superfat_percent=request.superfat_percent,
        additives=[
            AdditiveOutput(
                id=add.id,
                name=db_additives[add.id].common_name if add.id in db_additives else add.id,  # Note: AdditiveOutput uses 'name' (correct per spec)
                weight_g=round_to_precision(add.weight_g),
                percentage=round_to_precision(add.percentage)
            )
            for add in normalized_additives
        ] if request.additives else []
    )

    # Use authenticated user's ID
    user_id = current_user.id
    calculation_id = uuid4()
    timestamp = datetime.utcnow()

    # Step 11: Persist calculation to database (Task 3.3.2)
    # Fixed: Store complete data including base metrics, additive effects, and sat/unsat ratio
    db_calculation = Calculation(
        id=calculation_id,
        user_id=user_id,
        recipe_data={
            "total_oil_weight_g": total_oil_weight_g,
            "oils": [{"id": oil.id, "common_name": db_oils[oil.id].common_name, "weight_g": oil.weight_g, "percentage": oil.percentage} for oil in normalized_oils],
            "lye": {
                "naoh_weight_g": purity_result['commercial_naoh_g'],
                "koh_weight_g": purity_result['commercial_koh_g'],
                "total_lye_g": purity_result['total_lye_g'],
                "naoh_percent": request.lye.naoh_percent,
                "koh_percent": request.lye.koh_percent,
                "koh_purity": request.lye.koh_purity,
                "naoh_purity": request.lye.naoh_purity,
                "pure_koh_equivalent_g": purity_result['pure_koh_equivalent_g'],
                "pure_naoh_equivalent_g": purity_result['pure_naoh_equivalent_g']
            },
            "water_weight_g": water_g,
            "water_method": request.water.method,
            "water_method_value": request.water.value,
            "superfat_percent": request.superfat_percent,
            "additives": [{"id": add.id, "name": db_additives[add.id].common_name if add.id in db_additives else add.id, "weight_g": add.weight_g, "percentage": add.percentage} for add in normalized_additives] if request.additives else []
        },
        results_data={
            "quality_metrics": {
                "hardness": final_metrics.hardness,
                "cleansing": final_metrics.cleansing,
                "conditioning": final_metrics.conditioning,
                "bubbly_lather": final_metrics.bubbly_lather,
                "creamy_lather": final_metrics.creamy_lather,
                "longevity": final_metrics.longevity,
                "stability": final_metrics.stability,
                "iodine": round_to_precision(iodine_value),
                "ins": round_to_precision(ins_value)
            },
            "quality_metrics_base": {
                "hardness": base_metrics.hardness,
                "cleansing": base_metrics.cleansing,
                "conditioning": base_metrics.conditioning,
                "bubbly_lather": base_metrics.bubbly_lather,
                "creamy_lather": base_metrics.creamy_lather,
                "longevity": base_metrics.longevity,
                "stability": base_metrics.stability,
                "iodine": round_to_precision(iodine_value),
                "ins": round_to_precision(ins_value)
            },
            "additive_effects": [
                {
                    "additive_id": effect.additive_id,
                    "additive_name": effect.additive_name,
                    "effects": effect.effects,
                    "confidence": effect.confidence,
                    "verified_by_mga": effect.verified_by_mga
                }
                for effect in additive_effects_list
            ],
            "fatty_acid_profile": {
                "lauric": fatty_acid_profile.lauric,
                "myristic": fatty_acid_profile.myristic,
                "palmitic": fatty_acid_profile.palmitic,
                "stearic": fatty_acid_profile.stearic,
                "ricinoleic": fatty_acid_profile.ricinoleic,
                "oleic": fatty_acid_profile.oleic,
                "linoleic": fatty_acid_profile.linoleic,
                "linolenic": fatty_acid_profile.linolenic
            },
            "saturated_unsaturated_ratio": {
                "saturated": sat_unsat_ratio.saturated,
                "unsaturated": sat_unsat_ratio.unsaturated,
                "ratio": sat_unsat_ratio.ratio
            }
        }
    )

    db.add(db_calculation)
    await db.commit()

    return CalculationResponse(
        calculation_id=calculation_id,
        timestamp=timestamp,
        user_id=user_id,
        recipe=recipe_output,
        quality_metrics=QualityMetrics(
            hardness=final_metrics.hardness,
            cleansing=final_metrics.cleansing,
            conditioning=final_metrics.conditioning,
            bubbly_lather=final_metrics.bubbly_lather,
            creamy_lather=final_metrics.creamy_lather,
            longevity=final_metrics.longevity,
            stability=final_metrics.stability,
            iodine=round_to_precision(iodine_value),
            ins=round_to_precision(ins_value)
        ),
        quality_metrics_base=QualityMetrics(
            hardness=base_metrics.hardness,
            cleansing=base_metrics.cleansing,
            conditioning=base_metrics.conditioning,
            bubbly_lather=base_metrics.bubbly_lather,
            creamy_lather=base_metrics.creamy_lather,
            longevity=base_metrics.longevity,
            stability=base_metrics.stability,
            iodine=round_to_precision(iodine_value),
            ins=round_to_precision(ins_value)
        ),
        additive_effects=additive_effects_list,
        fatty_acid_profile=FattyAcidProfile(
            lauric=fatty_acid_profile.lauric,
            myristic=fatty_acid_profile.myristic,
            palmitic=fatty_acid_profile.palmitic,
            stearic=fatty_acid_profile.stearic,
            ricinoleic=fatty_acid_profile.ricinoleic,
            oleic=fatty_acid_profile.oleic,
            linoleic=fatty_acid_profile.linoleic,
            linolenic=fatty_acid_profile.linolenic
        ),
        saturated_unsaturated_ratio=SaturatedUnsaturatedRatio(
            saturated=sat_unsat_ratio.saturated,
            unsaturated=sat_unsat_ratio.unsaturated,
            ratio=sat_unsat_ratio.ratio
        ),
        warnings=warnings
    )


@router.get("/calculate/{id}", response_model=CalculationResponse, status_code=status.HTTP_200_OK)
async def get_calculation(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CalculationResponse:
    """
    Retrieve saved calculation by ID (Task 3.4.1).

    Args:
        id: Calculation UUID
        db: Database session

    Returns:
        Calculation response with all data

    Raises:
        HTTPException 404: Calculation not found
    """
    stmt = select(Calculation).where(Calculation.id == id)
    result = await db.execute(stmt)
    calculation = result.scalar_one_or_none()

    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Calculation with ID {id} not found"
                }
            }
        )

    # Validate ownership - user can only access their own calculations
    if calculation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Access denied - you don't own this calculation"
                }
            }
        )

    # Reconstruct response from stored data
    # Fixed: Complete deserialization of all stored data
    recipe_data = calculation.recipe_data
    results_data = calculation.results_data

    # Reconstruct recipe
    recipe = RecipeOutput(
        total_oil_weight_g=recipe_data["total_oil_weight_g"],
        oils=[OilOutput(**oil) for oil in recipe_data.get("oils", [])],
        lye=LyeOutput(**recipe_data["lye"]),
        water_weight_g=recipe_data["water_weight_g"],
        water_method=recipe_data["water_method"],
        water_method_value=recipe_data["water_method_value"],
        superfat_percent=recipe_data["superfat_percent"],
        additives=[AdditiveOutput(**add) for add in recipe_data.get("additives", [])]
    )

    # Reconstruct additive effects
    additive_effects = [
        AdditiveEffect(**effect) for effect in results_data.get("additive_effects", [])
    ]

    # Return complete response with all stored data
    return CalculationResponse(
        calculation_id=calculation.id,
        timestamp=calculation.created_at,
        user_id=calculation.user_id,
        recipe=recipe,
        quality_metrics=QualityMetrics(**results_data["quality_metrics"]),
        quality_metrics_base=QualityMetrics(**results_data.get("quality_metrics_base", results_data["quality_metrics"])),
        additive_effects=additive_effects,
        fatty_acid_profile=FattyAcidProfile(**results_data["fatty_acid_profile"]),
        saturated_unsaturated_ratio=SaturatedUnsaturatedRatio(**results_data.get("saturated_unsaturated_ratio", {"saturated": 0, "unsaturated": 0, "ratio": "0:0"})),
        warnings=[]  # Warnings not persisted, only generated at calculation time
    )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint (Task 3.5.1).

    Tests database connectivity.
    No authentication required.

    Returns:
        Health status
    """
    try:
        # Test database connection
        await db.execute(select(1))
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )
