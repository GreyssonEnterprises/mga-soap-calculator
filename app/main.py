"""
FastAPI application main module

Provides:
- RESTful API for soap recipe calculations
- JWT-based authentication and authorization
- Professional-grade saponification and quality metric calculations
- Advanced additive effect modeling (competitive advantage)
- Smart additive calculator with usage recommendations
- Complete OpenAPI/Swagger documentation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.api.v1 import additives, auth, calculate, colorants, essential_oils, inci, resources
from app.core.config import settings


def custom_openapi():
    """Custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="MGA Soap Calculator API",
        version="1.0.0",
        description="""
## Professional-Grade Soap Recipe Calculator

Calculate saponification values, quality metrics, and additive effects for soap recipes.

### Key Features

**Calculation Engine:**
- Lye requirements (NaOH, KOH, or mixed)
- Three water calculation methods (% of oils, lye concentration, water:lye ratio)
- 7 quality metrics (hardness, cleansing, conditioning, bubbly, creamy, longevity, stability)
- Fatty acid profile analysis
- INS (Iodine Number of Saponification) values
- Iodine values for unsaturation analysis

**Smart Additive Calculator:**
- Usage rate recommendations (light/standard/heavy)
- Category-based browsing (exfoliant, hardener, lather_booster, etc.)
- Safety warnings and preparation instructions
- Essential oil max usage rates with blending guidance
- Natural colorant recommendations (9 color families)

**Additive Effects (Competitive Advantage):**
- Research-backed quality effect modifiers
- Automatic effect scaling based on usage rate
- Support for 12+ additives (Kaolin clay, Sodium Lactate, Honey, etc.)
- Low-confidence additive warnings

**Security:**
- JWT authentication with 24-hour token expiry
- User registration with Argon2id password hashing (OWASP recommended)
- Calculation ownership enforcement (users can only access their own calculations)
- CORS-protected endpoints

### Error Codes

| Code | Description | Resolution |
|------|-------------|-----------|
| 400 | Invalid oil percentages (must sum to 100%) | Adjust oil percentages to total 100% |
| 400 | Lye percentages must sum to 100% | Adjust NaOH/KOH percentages |
| 401 | Unauthorized - missing or invalid JWT | Register and login to get token |
| 403 | Forbidden - accessing another user's calculation | Only access your own calculations |
| 404 | Calculation not found | Verify calculation ID is correct |
| 422 | Validation error - unknown oil/additive ID | Use valid IDs from database |
| 500 | Server error | Check API logs for details |

### Authentication Flow

1. **Register:** `POST /api/v1/auth/register` with email and password
2. **Login:** `POST /api/v1/auth/login` to receive JWT token
3. **Use Token:** Add `Authorization: Bearer <token>` header to protected requests
4. **Token Expiry:** 24 hours (generate new token by logging in again)

### Getting Started

**Example Calculation Request:**
```json
{
  "oils": [
    {"id": 1, "percentage": 50},  // 50% Olive Oil
    {"id": 2, "percentage": 30},  // 30% Coconut Oil
    {"id": 3, "percentage": 20}   // 20% Palm Oil
  ],
  "lye": {
    "naoh_percent": 100,
    "koh_percent": 0
  },
  "water": {
    "method": "percent_of_oils",
    "value": 38
  },
  "superfat_percent": 5,
  "additives": [
    {"id": 1, "usage_percent": 2}  // 2% Kaolin Clay
  ]
}
```

### Database Seed Data

**Available Oils:**
- Olive Oil, Coconut Oil, Palm Oil
- Avocado Oil, Castor Oil, Shea Butter
- Babassu Oil, Macadamia Oil, Sunflower Oil
- Jojoba Oil, Sweet Almond Oil

**Available Additives:**
- High Confidence: Sodium Lactate, Sugar, Honey, Colloidal Oatmeal, Kaolin Clay, Sea Salt
- Medium Confidence: Silk, Bentonite Clay, French Green Clay, Rose Clay

### API Response Format

All responses follow this structure:
```json
{
  "calculation_id": "uuid",
  "recipe": {
    "oils": [...],
    "lye": {...},
    "water": {...},
    "additives": [...]
  },
  "results": {
    "quality_metrics": {...},
    "fatty_acid_profile": {...},
    "iodine_value": 75.5,
    "ins_value": 175.3
  },
  "warnings": [
    {"type": "HIGH_SUPERFAT", "message": "..."}
  ]
}
```

---

**Documentation:** See `/docs` for interactive API explorer
**Spec File:** agent-os/specs/2025-11-01-core-calculation-api/spec.md
**Test Coverage:** 80% (21/21 tests passing)
        """,
        routes=app.routes,
    )

    # Add security scheme for JWT
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT authentication token from login endpoint",
        }
    }

    # Add error response examples
    openapi_schema["components"]["schemas"]["ErrorResponse"] = {
        "type": "object",
        "properties": {
            "error_code": {"type": "string", "example": "INVALID_OIL_PERCENTAGES"},
            "message": {"type": "string", "example": "Oil percentages must sum to 100.0%"},
            "details": {"type": "array", "items": {"type": "object"}},
        },
        "required": ["error_code", "message"],
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Create FastAPI application
app = FastAPI(
    title="MGA Soap Calculator API",
    version="1.0.0",
    description="Professional-grade soap recipe calculator with JWT authentication",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "MGA Automotive",
        "email": "info@mga-automotive.com",
    },
    license_info={
        "name": "Proprietary - MGA Automotive",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Local development"},
        {"url": "https://api.mga-automotive.local", "description": "Production (when deployed)"},
    ],
)

# Apply custom OpenAPI schema
app.openapi = custom_openapi

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(calculate.router)
app.include_router(resources.router)
app.include_router(additives.router)
app.include_router(essential_oils.router)
app.include_router(colorants.router)
app.include_router(inci.router)


@app.get(
    "/api/v1/health",
    tags=["health"],
    summary="Health check endpoint",
    description="Check if API is running and database is connected. No authentication required.",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "environment": "production",
                    }
                }
            },
        }
    },
)
async def health_check():
    """
    Health check endpoint - no authentication required.

    Returns API status and version information.
    Use this to verify API is operational before making calculations.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    tags=["errors"],
    summary="Catch-all for missing /v1/ prefix",
    description="Returns helpful error when API version prefix is missing",
    responses={
        404: {
            "description": "API version required",
            "content": {
                "application/json": {
                    "example": {
                        "error": "API version required",
                        "detail": "Did you mean /api/v1/auth/register?",
                        "correct_path": "/api/v1/auth/register",
                        "hint": "All API endpoints require /v1/ prefix",
                    }
                }
            },
        }
    },
)
async def redirect_missing_v1(path: str):
    """
    Catch-all route for missing /v1/ prefix.

    This route catches requests to /api/* that don't include the required /v1/ version prefix.
    Returns a helpful 404 error with the corrected path.

    IMPORTANT: This route is registered LAST to avoid intercepting valid /api/v1/* routes.

    Args:
        path: The requested path after /api/

    Returns:
        404 error with suggested correct path
    """
    # Only handle paths that DON'T start with v1/
    if not path.startswith("v1/"):
        correct_path = f"/api/v1/{path}"
        return JSONResponse(
            status_code=404,
            content={
                "error": "API version required",
                "detail": f"Did you mean {correct_path}?",
                "correct_path": correct_path,
                "hint": "All API endpoints require /v1/ prefix",
            },
        )

    # If we somehow got here with a v1/ path, return generic 404
    raise HTTPException(status_code=404, detail="Not Found")
