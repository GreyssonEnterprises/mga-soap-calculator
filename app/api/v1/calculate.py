"""
Calculation API endpoints (Tasks 3.3, 3.4, 3.5)

TDD Evidence: Tests written first in test_calculation_endpoint.py
Implements POST /api/v1/calculate, GET /api/v1/calculate/{id}, and
GET /api/v1/calculations (paginated list, scoped to the authenticated user).

CQ-08 / CI-03 refactor: The ``create_calculation`` handler delegates to the
three-stage pipeline in ``_calculation_pipeline`` (``resolve_inputs`` →
``compute_recipe`` → ``persist_calculation``). The endpoint keeps only HTTP
concerns (auth, status codes, response serialization).
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app import __version__
from app.api._pagination import paginate_query
from app.api.v1._calculation_pipeline import (
    build_response,
    compute_recipe,
    persist_calculation,
    resolve_inputs,
)
from app.core.security import get_current_user
from app.db import get_db
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.requests import CalculationRequest
from app.schemas.responses import (
    AdditiveEffect,
    AdditiveOutput,
    CalculationListResponse,
    CalculationResponse,
    CalculationSummary,
    FattyAcidProfile,
    LyeOutput,
    OilOutput,
    QualityMetrics,
    RecipeOutput,
    SaturatedUnsaturatedRatio,
)

router = APIRouter(prefix="/api/v1", tags=["calculations"])


@router.post("/calculate", response_model=CalculationResponse, status_code=status.HTTP_200_OK)
async def create_calculation(
    request: CalculationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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

    The heavy lifting is done by ``_calculation_pipeline``; this handler is a
    thin wrapper over that three-stage pipeline and handles HTTP concerns
    only.

    Args:
        request: Calculation request with oils, lye, water, superfat, additives
        db: Database session
        current_user: JWT-authenticated user

    Returns:
        Complete calculation response with all metrics

    Raises:
        HTTPException 400: Invalid oil percentages
        HTTPException 422: Unknown oil or additive IDs
    """
    # Stage 1 — validate + load DB data. Raises HTTPException on invalid input.
    inputs = await resolve_inputs(request, db)

    # Stage 2 — pure compute (no DB, no framework).
    computed = compute_recipe(inputs)

    # Stage 3 — persist. If the commit fails SQLAlchemy raises; FastAPI turns
    # that into a 500. Pure compute has already succeeded, so no DB state is
    # left in a half-written state.
    persisted = await persist_calculation(current_user, inputs, computed, db)

    return build_response(
        calculation_id=persisted.id,
        user_id=current_user.id,
        timestamp=persisted.created_at or datetime.utcnow(),
        computed=computed,
    )


@router.get("/calculate/{id}", response_model=CalculationResponse, status_code=status.HTTP_200_OK)
async def get_calculation(
    id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
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
                "error": {"code": "NOT_FOUND", "message": f"Calculation with ID {id} not found"}
            },
        )

    # Validate ownership - user can only access their own calculations
    if calculation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Access denied - you don't own this calculation",
                }
            },
        )

    # Reconstruct response from stored data
    recipe_data = calculation.recipe_data
    results_data = calculation.results_data

    recipe = RecipeOutput(
        total_oil_weight_g=recipe_data["total_oil_weight_g"],
        oils=[OilOutput(**oil) for oil in recipe_data.get("oils", [])],
        lye=LyeOutput(**recipe_data["lye"]),
        water_weight_g=recipe_data["water_weight_g"],
        water_method=recipe_data["water_method"],
        water_method_value=recipe_data["water_method_value"],
        superfat_percent=recipe_data["superfat_percent"],
        additives=[AdditiveOutput(**add) for add in recipe_data.get("additives", [])],
    )

    additive_effects = [
        AdditiveEffect(**effect) for effect in results_data.get("additive_effects", [])
    ]

    return CalculationResponse(
        calculation_id=calculation.id,
        timestamp=calculation.created_at,
        user_id=calculation.user_id,
        recipe=recipe,
        quality_metrics=QualityMetrics(**results_data["quality_metrics"]),
        quality_metrics_base=QualityMetrics(
            **results_data.get("quality_metrics_base", results_data["quality_metrics"])
        ),
        additive_effects=additive_effects,
        fatty_acid_profile=FattyAcidProfile(**results_data["fatty_acid_profile"]),
        saturated_unsaturated_ratio=SaturatedUnsaturatedRatio(
            **results_data.get(
                "saturated_unsaturated_ratio", {"saturated": 0, "unsaturated": 0, "ratio": "0:0"}
            )
        ),
        warnings=[],  # Warnings not persisted, only generated at calculation time
    )


@router.get(
    "/calculations",
    response_model=CalculationListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_calculations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Rows per page (1-100)."),
    offset: int = Query(0, ge=0, description="Rows to skip before this page."),
    sort_order: Literal["asc", "desc"] = Query(
        "desc",
        description=(
            "Sort direction on created_at. Default 'desc' so newest calculations appear first."
        ),
    ),
) -> CalculationListResponse:
    """List the authenticated user's saved calculations, paginated.

    Returns a lightweight summary per calculation — enough to render a "my
    recipes" list UI without replaying the full recipe JSON for every row.
    Use ``GET /api/v1/calculate/{id}`` to fetch full recipe + results for a
    specific calculation once the user picks one.

    Scoped to ``current_user.id``; there is no way to list another user's
    calculations through this endpoint (matches the 403 behavior of
    ``get_calculation``).

    Only ``created_at`` is sortable in this release — the UI need for sorting
    by batch size or quality metrics isn't established yet, and adding
    JSONB-casted sort columns is complexity we can earn later.
    """
    base_query = select(Calculation).where(Calculation.user_id == current_user.id)

    items, total_count, has_more = await paginate_query(
        db,
        base_query,
        sort_column=Calculation.created_at,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )

    summaries = [_summarize_calculation(calc) for calc in items]

    return CalculationListResponse(
        calculations=summaries,
        total_count=total_count,
        limit=limit,
        offset=offset,
        has_more=has_more,
    )


def _summarize_calculation(calc: Calculation) -> CalculationSummary:
    """Build a lightweight summary for the list endpoint.

    Reads from the persisted ``recipe_data`` / ``results_data`` JSONB so no
    recomputation is needed. Defensive about missing fields — earlier records
    from before the Phase 3 pipeline refactor may have slightly different
    shapes and should still render in a list.
    """
    recipe = calc.recipe_data or {}
    results = calc.results_data or {}

    oils = recipe.get("oils", [])
    top_oils = [
        o.get("common_name") or o.get("id", "unknown")
        for o in sorted(oils, key=lambda o: o.get("weight_g", 0.0), reverse=True)[:3]
    ]

    metrics = results.get("quality_metrics") or {
        "hardness": 0,
        "cleansing": 0,
        "conditioning": 0,
        "bubbly_lather": 0,
        "creamy_lather": 0,
        "longevity": 0,
        "stability": 0,
        "iodine": 0,
        "ins": 0,
    }

    return CalculationSummary(
        calculation_id=calc.id,
        created_at=calc.created_at,
        total_oil_weight_g=float(recipe.get("total_oil_weight_g", 0.0)),
        superfat_percent=float(recipe.get("superfat_percent", 0.0)),
        oil_count=len(oils),
        top_oils=top_oils,
        quality_metrics=QualityMetrics(**metrics),
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
        return {"status": "healthy", "database": "connected", "version": __version__}
    except SQLAlchemyError as e:
        # SQLAlchemyError is the root of all SQLAlchemy-raised exceptions and
        # covers connection loss, DBAPI errors (asyncpg), operational errors,
        # timeouts, and pool exhaustion. Anything else (e.g. asyncio
        # CancelledError) should propagate and let FastAPI return 500.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "database": "disconnected", "error": str(e)},
        )
