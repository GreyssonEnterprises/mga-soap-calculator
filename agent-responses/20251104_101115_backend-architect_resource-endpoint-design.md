# Resource Discovery Endpoints - Architecture Design

**Timestamp:** 2025-11-04T10:11:15
**Task:** Design RESTful resource discovery endpoints
**Requestor:** Bob

---

## Executive Summary

The MGA Soap Calculator API currently has zero discoverability. Users can't figure out what oils, additives, or lye types exist without reading external documentation or guessing IDs.

**Solution:** Add three clean REST endpoints for resource listing with practical pagination and optional filtering.

---

## Current State Analysis

### Models Structure

**Oil Model** (`app/models/oil.py`):
```python
- id: string (PK)
- common_name: string
- inci_name: string
- sap_value_naoh: float
- sap_value_koh: float
- iodine_value: float
- ins_value: float
- fatty_acids: JSONB (8 fatty acids)
- quality_contributions: JSONB (7 metrics)
- created_at: timestamp
- updated_at: timestamp
```

**Additive Model** (`app/models/additive.py`):
```python
- id: string (PK)
- common_name: string
- inci_name: string
- typical_usage_min_percent: float
- typical_usage_max_percent: float
- quality_effects: JSONB (7 metrics)
- confidence_level: string (high/medium/low)
- verified_by_mga: boolean
- safety_warnings: JSONB (optional)
- created_at: timestamp
- updated_at: timestamp
```

**Lye:** Not a separate model. NaOH/KOH percentages are request parameters, not database entities.

### Existing API Patterns

**Routing Structure:**
```
/api/v1/auth/register - POST
/api/v1/auth/login - POST
/api/v1/calculate - POST (authenticated)
/api/v1/calculate/{id} - GET (authenticated)
/api/v1/health - GET (unauthenticated)
```

**Conventions Observed:**
- Prefix: `/api/v1/`
- Router tags for OpenAPI grouping
- Response models with Pydantic
- Async/await with SQLAlchemy AsyncSession
- Consistent error structure with `error.code` and `error.message`
- Authentication via JWT bearer tokens (Depends on `get_current_user`)

---

## Endpoint Design

### 1. GET /api/v1/oils

**Purpose:** List all available oils with essential properties for recipe formulation.

**Authentication:** Optional (public data, but could require auth if desired)

**Query Parameters:**
```python
- limit: int = 50  # Pagination size (max 100)
- offset: int = 0  # Pagination offset
- search: Optional[str] = None  # Search by common_name or inci_name
- sort_by: Literal["common_name", "ins_value", "iodine_value"] = "common_name"
- sort_order: Literal["asc", "desc"] = "asc"
```

**Response Schema:**
```python
{
  "oils": [
    {
      "id": "coconut",
      "common_name": "Coconut Oil",
      "inci_name": "Cocos Nucifera Oil",
      "sap_value_naoh": 0.183,
      "sap_value_koh": 0.257,
      "iodine_value": 10.0,
      "ins_value": 258.0,
      "fatty_acids": {
        "lauric": 48.0,
        "myristic": 19.0,
        ...
      },
      "quality_contributions": {
        "hardness": 29.0,
        "cleansing": 67.0,
        ...
      }
    }
  ],
  "total_count": 42,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

**Filtering Logic:**
- `search`: Case-insensitive LIKE on `common_name` OR `inci_name`
- `sort_by`: Order by specified field
- Pagination: Standard limit/offset pattern

**Example Requests:**
```bash
# Get first 50 oils (default)
GET /api/v1/oils

# Search for "olive"
GET /api/v1/oils?search=olive

# Sort by INS value descending
GET /api/v1/oils?sort_by=ins_value&sort_order=desc

# Pagination
GET /api/v1/oils?limit=20&offset=40
```

---

### 2. GET /api/v1/lyes

**Purpose:** List available lye types (NaOH, KOH, mixed).

**Status:** Not needed as separate endpoint.

**Rationale:**
Lye is not a database entity. Users specify `naoh_percent` and `koh_percent` in calculation requests. The valid combinations are:
- 100% NaOH (hard bar soap)
- 100% KOH (liquid soap)
- Mixed (specialty soaps)

**Alternative:** Document lye configuration in API docs, not as a resource endpoint.

**If you really want this endpoint (not recommended):**
```python
GET /api/v1/lyes
Response:
{
  "lye_types": [
    {"name": "Sodium Hydroxide (NaOH)", "common_use": "Hard bar soap", "naoh_percent": 100, "koh_percent": 0},
    {"name": "Potassium Hydroxide (KOH)", "common_use": "Liquid soap", "naoh_percent": 0, "koh_percent": 100},
    {"name": "Mixed", "common_use": "Specialty formulations", "naoh_percent": "variable", "koh_percent": "variable"}
  ]
}
```

But honestly? This is better in documentation than as a database-backed endpoint.

---

### 3. GET /api/v1/additives

**Purpose:** List all available additives with usage guidelines and quality effects.

**Authentication:** Optional (public data)

**Query Parameters:**
```python
- limit: int = 50  # Pagination size (max 100)
- offset: int = 0  # Pagination offset
- search: Optional[str] = None  # Search by common_name or inci_name
- confidence: Optional[Literal["high", "medium", "low"]] = None  # Filter by confidence
- verified_only: bool = False  # Only show MGA-verified additives
- sort_by: Literal["common_name", "confidence_level"] = "common_name"
- sort_order: Literal["asc", "desc"] = "asc"
```

**Response Schema:**
```python
{
  "additives": [
    {
      "id": "kaolin_clay",
      "common_name": "Kaolin Clay",
      "inci_name": "Kaolin",
      "typical_usage_min_percent": 1.0,
      "typical_usage_max_percent": 3.0,
      "quality_effects": {
        "hardness": 2.0,
        "cleansing": 0.0,
        "conditioning": 1.0,
        ...
      },
      "confidence_level": "high",
      "verified_by_mga": true,
      "safety_warnings": {
        "skin_sensitivity": "May be drying for sensitive skin at high concentrations"
      }
    }
  ],
  "total_count": 28,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

**Filtering Logic:**
- `search`: Case-insensitive LIKE on `common_name` OR `inci_name`
- `confidence`: Exact match on `confidence_level` field
- `verified_only`: Filter where `verified_by_mga = true`
- `sort_by`: Order by specified field
- Pagination: Standard limit/offset

**Example Requests:**
```bash
# Get all additives
GET /api/v1/additives

# Only high-confidence additives
GET /api/v1/additives?confidence=high

# Only MGA-verified additives
GET /api/v1/additives?verified_only=true

# Search for "clay"
GET /api/v1/additives?search=clay

# Combine filters
GET /api/v1/additives?confidence=high&verified_only=true&search=clay
```

---

## Pagination Strategy

### When to Use Pagination

**Oils:** Likely 30-50 entries. Pagination optional but recommended for scalability.
**Additives:** Likely 20-40 entries. Pagination optional but recommended.
**Lyes:** Not applicable (not a database resource).

### Pagination Pattern

**Standard Limit/Offset:**
```python
- limit: max items per page (default 50, max 100)
- offset: skip N items (default 0)
- total_count: total matching items
- has_more: boolean indicating if more results exist
```

**Why Limit/Offset?**
- Simple implementation with SQLAlchemy
- Predictable for clients
- No complex cursor management needed
- Works fine for datasets <1000 items

**Alternative (Cursor-Based):** Only if you expect >1000 oils/additives. Not needed now.

---

## Response Schema Design

### Shared Response Wrapper

**Common Fields:**
```python
{
  "items": [...],  # Generic list of resources
  "total_count": int,
  "limit": int,
  "offset": int,
  "has_more": bool
}
```

### Resource-Specific Models

**OilResponse:**
```python
class OilListItem(BaseModel):
    id: str
    common_name: str
    inci_name: str
    sap_value_naoh: float
    sap_value_koh: float
    iodine_value: float
    ins_value: float
    fatty_acids: dict
    quality_contributions: dict

class OilListResponse(BaseModel):
    oils: List[OilListItem]
    total_count: int
    limit: int
    offset: int
    has_more: bool
```

**AdditiveResponse:**
```python
class AdditiveListItem(BaseModel):
    id: str
    common_name: str
    inci_name: str
    typical_usage_min_percent: float
    typical_usage_max_percent: float
    quality_effects: dict
    confidence_level: str
    verified_by_mga: bool
    safety_warnings: Optional[dict] = None

class AdditiveListResponse(BaseModel):
    additives: List[AdditiveListItem]
    total_count: int
    limit: int
    offset: int
    has_more: bool
```

---

## Implementation Guidance

### File Structure

**New Files:**
```
app/api/v1/resources.py  # New router for resource endpoints
app/schemas/resources.py # New response models
```

**Or separate files:**
```
app/api/v1/oils.py       # Oils endpoint
app/api/v1/additives.py  # Additives endpoint
app/schemas/oils.py      # Oil response models
app/schemas/additives.py # Additive response models
```

**Recommendation:** Single `resources.py` file for now (both endpoints are simple). Split later if they get complex.

### Router Setup

```python
# app/api/v1/resources.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal

from app.db.base import get_db
from app.models.oil import Oil
from app.models.additive import Additive
from app.schemas.resources import OilListResponse, OilListItem, AdditiveListResponse, AdditiveListItem

router = APIRouter(
    prefix="/api/v1",
    tags=["resources"]
)

@router.get("/oils", response_model=OilListResponse)
async def list_oils(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    sort_by: Literal["common_name", "ins_value", "iodine_value"] = "common_name",
    sort_order: Literal["asc", "desc"] = "asc",
    db: AsyncSession = Depends(get_db)
) -> OilListResponse:
    """List available oils with pagination and filtering"""
    # Implementation here

@router.get("/additives", response_model=AdditiveListResponse)
async def list_additives(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    confidence: Optional[Literal["high", "medium", "low"]] = None,
    verified_only: bool = False,
    sort_by: Literal["common_name", "confidence_level"] = "common_name",
    sort_order: Literal["asc", "desc"] = "asc",
    db: AsyncSession = Depends(get_db)
) -> AdditiveListResponse:
    """List available additives with pagination and filtering"""
    # Implementation here
```

### Database Query Pattern

**Oils Endpoint Logic:**
```python
# Build base query
query = select(Oil)

# Apply search filter
if search:
    search_pattern = f"%{search}%"
    query = query.where(
        (Oil.common_name.ilike(search_pattern)) |
        (Oil.inci_name.ilike(search_pattern))
    )

# Apply sorting
sort_column = getattr(Oil, sort_by)
if sort_order == "desc":
    query = query.order_by(sort_column.desc())
else:
    query = query.order_by(sort_column.asc())

# Get total count (before pagination)
count_query = select(func.count()).select_from(query.subquery())
total_count = (await db.execute(count_query)).scalar()

# Apply pagination
query = query.limit(limit).offset(offset)

# Execute
result = await db.execute(query)
oils = result.scalars().all()

# Build response
return OilListResponse(
    oils=[OilListItem.from_orm(oil) for oil in oils],
    total_count=total_count,
    limit=limit,
    offset=offset,
    has_more=(offset + limit) < total_count
)
```

**Additives Endpoint Logic:**
```python
# Build base query
query = select(Additive)

# Apply search filter
if search:
    search_pattern = f"%{search}%"
    query = query.where(
        (Additive.common_name.ilike(search_pattern)) |
        (Additive.inci_name.ilike(search_pattern))
    )

# Apply confidence filter
if confidence:
    query = query.where(Additive.confidence_level == confidence)

# Apply verified filter
if verified_only:
    query = query.where(Additive.verified_by_mga == True)

# Apply sorting
sort_column = getattr(Additive, sort_by)
if sort_order == "desc":
    query = query.order_by(sort_column.desc())
else:
    query = query.order_by(sort_column.asc())

# Get total count
count_query = select(func.count()).select_from(query.subquery())
total_count = (await db.execute(count_query)).scalar()

# Apply pagination
query = query.limit(limit).offset(offset)

# Execute
result = await db.execute(query)
additives = result.scalars().all()

# Build response
return AdditiveListResponse(
    additives=[AdditiveListItem.from_orm(additive) for additive in additives],
    total_count=total_count,
    limit=limit,
    offset=offset,
    has_more=(offset + limit) < total_count
)
```

### Integration with Main App

**app/main.py:**
```python
from app.api.v1 import auth, calculate, resources  # Add resources

app.include_router(auth.router)
app.include_router(calculate.router)
app.include_router(resources.router)  # Add this line
```

---

## OpenAPI/Swagger Examples

### Oils Endpoint

**OpenAPI Spec:**
```yaml
/api/v1/oils:
  get:
    summary: List available oils
    description: Get paginated list of oils with optional search and sorting
    tags:
      - resources
    parameters:
      - name: limit
        in: query
        schema:
          type: integer
          default: 50
          minimum: 1
          maximum: 100
      - name: offset
        in: query
        schema:
          type: integer
          default: 0
          minimum: 0
      - name: search
        in: query
        schema:
          type: string
        description: Search by common name or INCI name
      - name: sort_by
        in: query
        schema:
          type: string
          enum: [common_name, ins_value, iodine_value]
          default: common_name
      - name: sort_order
        in: query
        schema:
          type: string
          enum: [asc, desc]
          default: asc
    responses:
      200:
        description: Successful response
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OilListResponse'
            example:
              oils:
                - id: "coconut"
                  common_name: "Coconut Oil"
                  inci_name: "Cocos Nucifera Oil"
                  sap_value_naoh: 0.183
                  sap_value_koh: 0.257
                  iodine_value: 10.0
                  ins_value: 258.0
                  fatty_acids:
                    lauric: 48.0
                    myristic: 19.0
                  quality_contributions:
                    hardness: 29.0
                    cleansing: 67.0
              total_count: 42
              limit: 50
              offset: 0
              has_more: false
```

### Additives Endpoint

**OpenAPI Spec:**
```yaml
/api/v1/additives:
  get:
    summary: List available additives
    description: Get paginated list of additives with optional filtering
    tags:
      - resources
    parameters:
      - name: limit
        in: query
        schema:
          type: integer
          default: 50
          minimum: 1
          maximum: 100
      - name: offset
        in: query
        schema:
          type: integer
          default: 0
          minimum: 0
      - name: search
        in: query
        schema:
          type: string
      - name: confidence
        in: query
        schema:
          type: string
          enum: [high, medium, low]
      - name: verified_only
        in: query
        schema:
          type: boolean
          default: false
      - name: sort_by
        in: query
        schema:
          type: string
          enum: [common_name, confidence_level]
          default: common_name
      - name: sort_order
        in: query
        schema:
          type: string
          enum: [asc, desc]
          default: asc
    responses:
      200:
        description: Successful response
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AdditiveListResponse'
            example:
              additives:
                - id: "kaolin_clay"
                  common_name: "Kaolin Clay"
                  inci_name: "Kaolin"
                  typical_usage_min_percent: 1.0
                  typical_usage_max_percent: 3.0
                  quality_effects:
                    hardness: 2.0
                    cleansing: 0.0
                  confidence_level: "high"
                  verified_by_mga: true
                  safety_warnings:
                    skin_sensitivity: "May be drying at high concentrations"
              total_count: 28
              limit: 50
              offset: 0
              has_more: false
```

---

## Example Request/Response Pairs

### GET /api/v1/oils (default)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/oils"
```

**Response (200 OK):**
```json
{
  "oils": [
    {
      "id": "coconut",
      "common_name": "Coconut Oil",
      "inci_name": "Cocos Nucifera Oil",
      "sap_value_naoh": 0.183,
      "sap_value_koh": 0.257,
      "iodine_value": 10.0,
      "ins_value": 258.0,
      "fatty_acids": {
        "lauric": 48.0,
        "myristic": 19.0,
        "palmitic": 9.0,
        "stearic": 3.0,
        "ricinoleic": 0.0,
        "oleic": 8.0,
        "linoleic": 2.0,
        "linolenic": 0.0
      },
      "quality_contributions": {
        "hardness": 29.0,
        "cleansing": 67.0,
        "conditioning": 10.0,
        "bubbly_lather": 67.0,
        "creamy_lather": 29.0,
        "longevity": 29.0,
        "stability": 77.0
      }
    },
    {
      "id": "olive",
      "common_name": "Olive Oil",
      "inci_name": "Olea Europaea Fruit Oil",
      "sap_value_naoh": 0.135,
      "sap_value_koh": 0.190,
      "iodine_value": 85.0,
      "ins_value": 109.0,
      "fatty_acids": {
        "lauric": 0.0,
        "myristic": 0.0,
        "palmitic": 11.0,
        "stearic": 4.0,
        "ricinoleic": 0.0,
        "oleic": 72.0,
        "linoleic": 10.0,
        "linolenic": 1.0
      },
      "quality_contributions": {
        "hardness": 17.0,
        "cleansing": 0.0,
        "conditioning": 82.0,
        "bubbly_lather": 0.0,
        "creamy_lather": 17.0,
        "longevity": 17.0,
        "stability": 83.0
      }
    }
  ],
  "total_count": 42,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

### GET /api/v1/oils?search=olive

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/oils?search=olive"
```

**Response (200 OK):**
```json
{
  "oils": [
    {
      "id": "olive",
      "common_name": "Olive Oil",
      "inci_name": "Olea Europaea Fruit Oil",
      "sap_value_naoh": 0.135,
      "sap_value_koh": 0.190,
      "iodine_value": 85.0,
      "ins_value": 109.0,
      "fatty_acids": {...},
      "quality_contributions": {...}
    }
  ],
  "total_count": 1,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

### GET /api/v1/additives?confidence=high&verified_only=true

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/additives?confidence=high&verified_only=true"
```

**Response (200 OK):**
```json
{
  "additives": [
    {
      "id": "kaolin_clay",
      "common_name": "Kaolin Clay",
      "inci_name": "Kaolin",
      "typical_usage_min_percent": 1.0,
      "typical_usage_max_percent": 3.0,
      "quality_effects": {
        "hardness": 2.0,
        "cleansing": 0.0,
        "conditioning": 1.0,
        "bubbly_lather": 0.0,
        "creamy_lather": 1.0,
        "longevity": 2.0,
        "stability": 1.0
      },
      "confidence_level": "high",
      "verified_by_mga": true,
      "safety_warnings": {
        "skin_sensitivity": "May be drying for sensitive skin at high concentrations"
      }
    },
    {
      "id": "sodium_lactate",
      "common_name": "Sodium Lactate",
      "inci_name": "Sodium Lactate",
      "typical_usage_min_percent": 1.0,
      "typical_usage_max_percent": 3.0,
      "quality_effects": {
        "hardness": 5.0,
        "cleansing": 0.0,
        "conditioning": 0.0,
        "bubbly_lather": 0.0,
        "creamy_lather": 0.0,
        "longevity": 3.0,
        "stability": 2.0
      },
      "confidence_level": "high",
      "verified_by_mga": true,
      "safety_warnings": null
    }
  ],
  "total_count": 8,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

---

## Performance Considerations

### Database Indexes

**Already Exists:**
- Primary keys on `id` (automatic)
- Timestamps indexed for common queries

**Recommended New Indexes:**
```sql
-- Oils
CREATE INDEX idx_oils_common_name ON oils(common_name);
CREATE INDEX idx_oils_ins_value ON oils(ins_value);
CREATE INDEX idx_oils_iodine_value ON oils(iodine_value);

-- Additives
CREATE INDEX idx_additives_common_name ON additives(common_name);
CREATE INDEX idx_additives_confidence ON additives(confidence_level);
CREATE INDEX idx_additives_verified ON additives(verified_by_mga);
```

**Why:**
- `common_name` indexes: Support search and sorting
- Numeric indexes: Support sorting by SAP/INS/Iodine values
- Confidence/verified indexes: Support filtering queries

### Query Optimization

**Count Optimization:**
Current approach uses subquery for counting. For small datasets (<1000 rows), this is fine.

**Alternative (if performance becomes an issue):**
- Cache total counts
- Use `EXPLAIN ANALYZE` to verify query plans
- Consider materialized views for complex filters

### Caching Strategy

**Not needed initially** (datasets are small and change infrequently).

**If you add caching later:**
- Redis cache for full oil/additive lists (TTL: 1 hour)
- Invalidate on database updates
- Cache key: `oils:list:{search}:{sort}` pattern

---

## Testing Requirements

### Unit Tests

**app/tests/test_resources_endpoint.py:**
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_oils_default(client: AsyncClient):
    """Test oils endpoint with default parameters"""
    response = await client.get("/api/v1/oils")
    assert response.status_code == 200
    data = response.json()
    assert "oils" in data
    assert "total_count" in data
    assert data["limit"] == 50
    assert data["offset"] == 0

@pytest.mark.asyncio
async def test_list_oils_search(client: AsyncClient):
    """Test oils search functionality"""
    response = await client.get("/api/v1/oils?search=olive")
    assert response.status_code == 200
    data = response.json()
    oils = data["oils"]
    assert all("olive" in oil["common_name"].lower() or
               "olive" in oil["inci_name"].lower()
               for oil in oils)

@pytest.mark.asyncio
async def test_list_oils_pagination(client: AsyncClient):
    """Test oils pagination"""
    response = await client.get("/api/v1/oils?limit=10&offset=5")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 10
    assert data["offset"] == 5
    assert len(data["oils"]) <= 10

@pytest.mark.asyncio
async def test_list_additives_filters(client: AsyncClient):
    """Test additive filtering by confidence and verification"""
    response = await client.get("/api/v1/additives?confidence=high&verified_only=true")
    assert response.status_code == 200
    data = response.json()
    additives = data["additives"]
    assert all(add["confidence_level"] == "high" for add in additives)
    assert all(add["verified_by_mga"] is True for add in additives)

@pytest.mark.asyncio
async def test_list_additives_sorting(client: AsyncClient):
    """Test additive sorting"""
    response = await client.get("/api/v1/additives?sort_by=common_name&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    names = [add["common_name"] for add in data["additives"]]
    assert names == sorted(names)
```

### Integration Tests

**Manual Testing Checklist:**
- [ ] GET /api/v1/oils returns all oils
- [ ] Search filtering works correctly
- [ ] Sorting by different fields works
- [ ] Pagination limit/offset works
- [ ] has_more flag accurate
- [ ] GET /api/v1/additives returns all additives
- [ ] Confidence filtering works
- [ ] Verified-only filtering works
- [ ] Combined filters work correctly
- [ ] Response schema matches OpenAPI spec

---

## Security Considerations

### Authentication

**Current Decision:** Public endpoints (no authentication required).

**Rationale:**
- Oil/additive data is public reference information
- No user-specific data exposure
- Similar to `/health` endpoint pattern

**Alternative:** Require authentication if you want to:
- Track API usage per user
- Rate-limit by user account
- Restrict access to premium ingredient database

**Implementation (if auth required):**
```python
@router.get("/oils", response_model=OilListResponse)
async def list_oils(
    ...,
    current_user: User = Depends(get_current_user),  # Add this
    db: AsyncSession = Depends(get_db)
):
```

### Rate Limiting

**Not implemented yet** but recommended for production:
- 100 requests/minute per IP for unauthenticated
- 1000 requests/minute for authenticated users
- Use FastAPI middleware or API gateway

### Input Validation

**Already handled by FastAPI:**
- Query params validated via `Query()` with min/max
- Enum validation for `sort_by`, `sort_order`, `confidence`
- Integer bounds for `limit` (1-100) and `offset` (≥0)

**SQL Injection:** Not a risk (SQLAlchemy ORM prevents this).

**Search Injection:** Using parameterized queries with `ilike()` - safe.

---

## Migration Path

### Database Changes

**None required.** Existing Oil and Additive tables have all needed fields.

**Optional Index Creation:**
```sql
-- Add after implementation if performance testing shows need
CREATE INDEX idx_oils_common_name ON oils(common_name);
CREATE INDEX idx_additives_confidence ON additives(confidence_level);
```

### Deployment Steps

1. **Create schemas:** `app/schemas/resources.py`
2. **Create router:** `app/api/v1/resources.py`
3. **Register router:** Update `app/main.py`
4. **Write tests:** `app/tests/test_resources_endpoint.py`
5. **Run tests:** `pytest app/tests/test_resources_endpoint.py`
6. **Manual testing:** Use Swagger UI at `/docs`
7. **Deploy:** Standard deployment process

### Backward Compatibility

**No breaking changes.** These are new endpoints - existing functionality unaffected.

---

## Future Enhancements

### Phase 2 (Optional)

**Individual Resource Endpoints:**
```python
GET /api/v1/oils/{id}      # Get single oil details
GET /api/v1/additives/{id} # Get single additive details
```

**Use Case:** Frontend detail pages or direct ID lookups.

**Rationale for Later:** List endpoints already return complete data. Single-resource endpoints add minimal value until you have partial response needs.

### Phase 3 (Optional)

**Advanced Filtering:**
```python
GET /api/v1/oils?min_ins=100&max_ins=200  # INS range filtering
GET /api/v1/oils?fatty_acid=lauric&min_percent=40  # Fatty acid filtering
```

**Category Endpoints:**
```python
GET /api/v1/oils/categories  # Group oils by type (coconut, palm, olive, etc.)
```

**Recommendations:**
```python
GET /api/v1/oils/recommended?superfat=5&hardness=min:30  # AI-suggested oils
```

**Rationale:** Wait for user demand. Don't build features nobody asked for.

---

## Summary for python-expert

### What to Implement

**Files to Create:**
1. `app/schemas/resources.py` - Response models (OilListItem, OilListResponse, AdditiveListItem, AdditiveListResponse)
2. `app/api/v1/resources.py` - Router with two endpoints (list_oils, list_additives)

**Files to Modify:**
1. `app/main.py` - Add `from app.api.v1 import resources` and `app.include_router(resources.router)`

**Testing:**
1. `app/tests/test_resources_endpoint.py` - Comprehensive tests for both endpoints

### Key Implementation Points

**Oils Endpoint:**
- Query params: limit, offset, search, sort_by, sort_order
- Search: Case-insensitive LIKE on common_name OR inci_name
- Sort: Support common_name, ins_value, iodine_value
- Return: Full oil data including fatty_acids and quality_contributions

**Additives Endpoint:**
- Query params: limit, offset, search, confidence, verified_only, sort_by, sort_order
- Search: Case-insensitive LIKE on common_name OR inci_name
- Filters: confidence (exact match), verified_by_mga (boolean)
- Sort: Support common_name, confidence_level
- Return: Full additive data including quality_effects and safety_warnings

**Pagination:**
- Standard limit/offset pattern
- Default limit: 50, max: 100
- Include total_count and has_more in responses

**No Authentication Required:** Public endpoints for reference data.

### Database Queries

**Pattern:**
```python
# 1. Build query with filters
query = select(Model).where(...)

# 2. Get total count before pagination
count_query = select(func.count()).select_from(query.subquery())
total_count = (await db.execute(count_query)).scalar()

# 3. Apply pagination
query = query.limit(limit).offset(offset)

# 4. Execute and build response
result = await db.execute(query)
items = result.scalars().all()
```

### Testing Checklist

- [ ] Default queries work (no params)
- [ ] Search filtering works
- [ ] Sorting works (all sort_by options)
- [ ] Pagination works (limit/offset)
- [ ] has_more flag accurate
- [ ] Confidence filtering works (additives)
- [ ] Verified-only filtering works (additives)
- [ ] Combined filters work
- [ ] Empty results handled gracefully
- [ ] Invalid params rejected by FastAPI

---

## Final Notes

This is a straightforward REST resource listing implementation. No fancy algorithms, no complex business logic, just clean database queries with pagination.

**Keep it simple:**
- No caching (yet)
- No rate limiting (yet)
- No authentication (public data)
- No cursor pagination (limit/offset is fine)
- No single-resource endpoints (list provides full data)

**Focus on:**
- Clean code
- Good tests
- Consistent patterns with existing API
- FastAPI best practices

Ship it, then iterate based on real usage.

---

**Status:** Complete
**Confidence:** High
**Follow-up:** Ready for python-expert implementation
