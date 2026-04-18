"""
INCI label generation API endpoints

User Story 1: Generate INCI labels for soap formulations
Spec 003: Generate three-format INCI labels from saved calculations
"""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.calculation import Calculation
from app.models.oil import Oil
from app.schemas.inci_label import (
    InciIngredient,
    InciLabelRequest,
    InciLabelResponse,
    ThreeFormatInciResponse,
)
from app.services.label_generator import generate_inci_label
from app.services.three_format_inci_generator import generate_three_format_labels

router = APIRouter(prefix="/api/v1/inci", tags=["INCI Labels"])


@router.post(
    "/generate-label",
    response_model=InciLabelResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate INCI label for soap formulation",
    description="""
Generate a complete INCI label for a soap formulation.

The endpoint:
1. Validates oil IDs exist in database
2. Calculates percentage of each oil
3. Generates saponified INCI names
4. Sorts ingredients by percentage (descending)
5. Returns formatted INCI label string + detailed ingredient list

INCI labels list ingredients in descending order by percentage.
    """,
)
async def generate_inci_label_endpoint(
    request: InciLabelRequest, db: AsyncSession = Depends(get_db)
):
    """
    Generate INCI label for soap formulation.

    **Request Body:**
    - formulation.oils: List of oils with weights
    - lye_type: 'naoh' or 'koh'

    **Response:**
    - inci_label: Comma-separated INCI names (sorted by %)
    - ingredients: Detailed list with percentages
    - total_oil_weight: Total grams of oils
    - lye_type_used: Echo of lye_type parameter

    **Example:**
    ```json
    {
      "formulation": {
        "oils": [
          {"oil_id": "coconut-oil", "weight_grams": 300},
          {"oil_id": "olive-oil", "weight_grams": 700}
        ]
      },
      "lye_type": "naoh"
    }
    ```

    **Returns:**
    ```json
    {
      "inci_label": "Sodium Olivate, Sodium Cocoate",
      "ingredients": [
        {
          "oil_id": "olive-oil",
          "common_name": "Olive Oil",
          "saponified_inci_name": "Sodium Olivate",
          "percentage": 70.0,
          "is_generated": false
        },
        {
          "oil_id": "coconut-oil",
          "common_name": "Coconut Oil",
          "saponified_inci_name": "Sodium Cocoate",
          "percentage": 30.0,
          "is_generated": false
        }
      ],
      "total_oil_weight": 1000.0,
      "lye_type_used": "naoh"
    }
    ```
    """
    # Step 1: Extract oil IDs and weights
    oil_ids = [item.oil_id for item in request.formulation.oils]
    oil_weights: dict[str, Decimal] = {
        item.oil_id: Decimal(str(item.weight_grams)) for item in request.formulation.oils
    }

    # Step 2: Fetch oils from database
    result = await db.execute(select(Oil).where(Oil.id.in_(oil_ids)))
    oils_list = result.scalars().all()

    # Verify all oils were found
    if len(oils_list) != len(oil_ids):
        found_ids = {oil.id for oil in oils_list}
        missing_ids = set(oil_ids) - found_ids
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Oil(s) not found in database: {', '.join(missing_ids)}",
        )

    # Create oil lookup dictionary
    oils_dict = {oil.id: oil for oil in oils_list}

    # Step 3: Generate INCI label
    try:
        inci_label, ingredient_details = generate_inci_label(
            oil_weights=oil_weights, oils_dict=oils_dict, lye_type=request.lye_type
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Step 4: Calculate total oil weight
    total_weight = sum(oil_weights.values())

    # Step 5: Format response
    ingredients = [
        InciIngredient(
            oil_id=detail.oil_id,
            common_name=detail.common_name,
            saponified_inci_name=detail.saponified_inci_name,
            percentage=detail.percentage,
            is_generated=detail.is_generated,
        )
        for detail in ingredient_details
    ]

    return InciLabelResponse(
        inci_label=inci_label,
        ingredients=ingredients,
        total_oil_weight=float(total_weight),
        lye_type_used=request.lye_type,
    )


# ============================================================================
# Spec 003: Calculation-Based Three-Format INCI Label Endpoint
# ============================================================================


@router.get(
    "/calculations/{calculation_id}/inci-label",
    response_model=ThreeFormatInciResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate INCI label for saved calculation (recipe)",
    description="""
Generate INCI ingredient labels in multiple formats for a saved calculation.

Returns up to three label formats:
- **raw_inci**: Pre-saponification format (oils + lye as separate ingredients)
- **saponified_inci**: Post-saponification format (sodium/potassium salts, lye excluded)
- **common_names**: Consumer-friendly ingredient names

All ingredients sorted by percentage (descending) per regulatory requirements.

Query Parameters:
- **format**: Which formats to return (all, raw_inci, saponified_inci, common_names)
- **include_percentages**: Add percentage values to label strings
- **line_by_line**: Use newline separation instead of commas

Example:
```
GET /api/v1/inci/calculations/123e4567-e89b-12d3-a456-426614174000/inci-label?format=all
```
    """,
)
async def get_calculation_inci_label(
    calculation_id: UUID,
    format: str = Query("all", regex="^(all|raw_inci|saponified_inci|common_names)$"),
    include_percentages: bool = Query(False),
    line_by_line: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate INCI label for a saved calculation (recipe).

    This endpoint fulfills Spec 003 requirement for recipe-based INCI generation.
    Unlike the formulation-based POST endpoint, this works with saved calculations.

    **Path Parameters:**
    - calculation_id: UUID of saved calculation

    **Query Parameters:**
    - format: "all" (default), "raw_inci", "saponified_inci", or "common_names"
    - include_percentages: Include percentage values in labels (default: false)
    - line_by_line: Newline-separated instead of comma-separated (default: false)

    **Returns:**
    - raw_inci: Pre-saponification INCI (if format=all or format=raw_inci)
    - saponified_inci: Post-saponification INCI (if format=all or format=saponified_inci)
    - common_names: Consumer-friendly names (if format=all or format=common_names)
    - ingredients_breakdown: Detailed list with percentages (always included)

    **Errors:**
    - 404: Calculation not found
    - 422: Invalid format parameter
    """
    # Step 1: Fetch calculation from database
    result = await db.execute(select(Calculation).where(Calculation.id == calculation_id))
    calculation = result.scalar_one_or_none()

    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calculation with ID {calculation_id} not found",
        )

    # Step 2: Extract recipe data from calculation
    recipe_data = calculation.recipe_data

    # Step 3: Fetch oils used in recipe
    oil_ids = [item["oil_id"] for item in recipe_data.get("oils", [])]

    if not oil_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Calculation contains no oils"
        )

    result = await db.execute(select(Oil).where(Oil.id.in_(oil_ids)))
    oils_list = result.scalars().all()

    # Verify all oils were found
    if len(oils_list) != len(oil_ids):
        found_ids = {oil.id for oil in oils_list}
        missing_ids = set(oil_ids) - found_ids
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Oil(s) not found in database: {', '.join(missing_ids)}",
        )

    # Create oil lookup dictionary
    oils_dict = {oil.id: oil for oil in oils_list}

    # Step 4: Generate three-format labels
    try:
        raw_inci, saponified_inci, common_names, breakdown = generate_three_format_labels(
            recipe_data=recipe_data,
            oils_dict=oils_dict,
            format_filter=format,
            include_percentages=include_percentages,
            line_by_line=line_by_line,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Step 5: Return response
    return ThreeFormatInciResponse(
        raw_inci=raw_inci,
        saponified_inci=saponified_inci,
        common_names=common_names,
        ingredients_breakdown=breakdown if format == "all" or include_percentages else None,
    )
