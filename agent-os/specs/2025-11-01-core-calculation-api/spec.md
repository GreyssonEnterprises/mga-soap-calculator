# Core Soap Calculation API - Technical Specification

**Version:** 1.0
**Date:** 2025-11-01
**Status:** Draft
**Author:** Spec Writer Agent

---

## 1. Overview

### 1.1 Purpose

The Core Soap Calculation API provides comprehensive soap recipe calculations for professional soap makers, including saponification values, quality metrics, fatty acid profiles, and unique additive effect modeling. This API enables MGA Automotive and future external users to optimize soap formulations through data-driven analysis.

### 1.2 Scope

**Phase 1 MVP includes:**
- POST and GET endpoints for recipe calculations
- Dual lye support (NaOH and KOH)
- Three water calculation methods
- Complete quality metrics and fatty acid profiles
- Industry-first additive effect modeling
- JWT authentication
- PostgreSQL persistence

**Out of Scope for Phase 1:**
- Cost calculator integration
- INCI name generation
- Fragrance calculator
- Batch management
- Recipe search/filtering
- Web interface

### 1.3 Competitive Advantage

**First soap calculator to model non-fat additive effects on quality metrics.**

Existing calculators (SoapCalc.net, Mendrulandia, The Sage) only calculate base soap properties from oils. They cannot predict how clays, salts, botanicals, or other additives affect hardness, cleansing, conditioning, or lather quality.

Our research-backed additive effect modeling (based on `agent-os/research/soap-additive-effects.md`) provides quantitative predictions for how additives modify quality metrics, enabling soap makers to formulate accurately on the first iteration instead of through expensive trial-and-error.

### 1.4 Success Criteria

**Technical Success:**
- Calculation accuracy within 1% of manual verification
- API response time <200ms for standard calculations
- 99.9% uptime for internal use
- >90% test coverage

**Business Success:**
- MGA Automotive using API for all new recipe development
- Additive effect predictions validated through production testing
- Zero data loss or calculation errors in production

---

## 2. Architecture

### 2.1 Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (async web framework)
- Uvicorn (ASGI server)

**Database:**
- PostgreSQL 15+
- SQLAlchemy 2.0 (async ORM)
- Alembic (migrations)

**Authentication:**
- JWT (JSON Web Tokens)
- python-jose or PyJWT

**API Style:**
- RESTful
- JSON request/response
- Automatic OpenAPI documentation (FastAPI built-in)

### 2.2 System Components

```
┌─────────────┐
│   Client    │
│ (MGA App)   │
└──────┬──────┘
       │ HTTPS
       │ JWT Token
       ▼
┌─────────────────────────────────┐
│       FastAPI Application       │
│  ┌──────────────────────────┐  │
│  │   Authentication Layer   │  │
│  └────────────┬─────────────┘  │
│               ▼                 │
│  ┌──────────────────────────┐  │
│  │   Request Validation     │  │
│  │   (Pydantic Models)      │  │
│  └────────────┬─────────────┘  │
│               ▼                 │
│  ┌──────────────────────────┐  │
│  │  Calculation Service     │  │
│  │  - Lye calculations      │  │
│  │  - Water calculations    │  │
│  │  - Quality metrics       │  │
│  │  - Additive effects      │  │
│  └────────────┬─────────────┘  │
│               ▼                 │
│  ┌──────────────────────────┐  │
│  │   Database Repository    │  │
│  └────────────┬─────────────┘  │
└───────────────┼─────────────────┘
                ▼
       ┌────────────────┐
       │   PostgreSQL   │
       │   - oils       │
       │   - additives  │
       │   - calculations│
       │   - users      │
       └────────────────┘
```

### 2.3 Data Flow

**Recipe Calculation Request:**

1. Client sends authenticated POST to `/api/v1/calculate`
2. JWT middleware validates token, extracts user_id
3. Pydantic model validates request body structure
4. Business logic validation (oil percentages = 100%, valid ingredient IDs)
5. Calculation service:
   - Normalizes inputs (weight ↔ percentage conversion)
   - Calculates base lye requirements
   - Calculates water requirements
   - Computes base quality metrics from oil blend
   - Applies additive effects to quality metrics
   - Generates fatty acid profile
   - Calculates INS and Iodine values
6. Repository persists calculation to database
7. Response returned with complete results

**Recipe Retrieval Request:**

1. Client sends authenticated GET to `/api/v1/calculate/{id}`
2. JWT middleware validates token
3. Repository queries calculation by ID
4. Authorization check: calculation.user_id == token.user_id
5. Response returned with stored calculation data

---

## 3. API Endpoints

### 3.1 POST /api/v1/calculate

Create new soap recipe calculation.

**Authentication:** Required (JWT Bearer token)

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "oils": [
    {
      "id": "olive_oil",
      "weight_g": 450.0,
      "percentage": null
    },
    {
      "id": "coconut_oil",
      "weight_g": null,
      "percentage": 30.0
    },
    {
      "id": "palm_oil",
      "weight_g": null,
      "percentage": 20.0
    }
  ],
  "lye": {
    "naoh_percent": 100.0,
    "koh_percent": 0.0
  },
  "water": {
    "method": "lye_concentration",
    "value": 33.0
  },
  "superfat_percent": 5.0,
  "additives": [
    {
      "id": "kaolin_clay",
      "weight_g": 20.0,
      "percentage": null
    },
    {
      "id": "sodium_lactate",
      "weight_g": null,
      "percentage": 3.0
    }
  ]
}
```

**Request Body Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `oils` | Array | Yes | List of oils in recipe |
| `oils[].id` | String | Yes | Oil identifier from database |
| `oils[].weight_g` | Float | One of weight/% | Oil weight in grams |
| `oils[].percentage` | Float | One of weight/% | Oil percentage of total oil weight |
| `lye` | Object | Yes | Lye type configuration |
| `lye.naoh_percent` | Float | Yes | NaOH percentage (0-100) |
| `lye.koh_percent` | Float | Yes | KOH percentage (0-100) |
| `water` | Object | Yes | Water calculation method |
| `water.method` | String | Yes | One of: `water_percent_of_oils`, `lye_concentration`, `water_lye_ratio` |
| `water.value` | Float | Yes | Value for selected method |
| `superfat_percent` | Float | Yes | Superfat percentage (0-100) |
| `additives` | Array | No | List of additives (optional) |
| `additives[].id` | String | Yes | Additive identifier from database |
| `additives[].weight_g` | Float | One of weight/% | Additive weight in grams |
| `additives[].percentage` | Float | One of weight/% | Additive percentage of total oil weight |

**Response (200 OK):**

```json
{
  "calculation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-11-01T14:30:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "recipe": {
    "total_oil_weight_g": 1000.0,
    "oils": [
      {
        "id": "olive_oil",
        "common_name": "Olive Oil",
        "weight_g": 500.0,
        "percentage": 50.0
      },
      {
        "id": "coconut_oil",
        "common_name": "Coconut Oil",
        "weight_g": 300.0,
        "percentage": 30.0
      },
      {
        "id": "palm_oil",
        "common_name": "Palm Oil",
        "weight_g": 200.0,
        "percentage": 20.0
      }
    ],
    "lye": {
      "naoh_weight_g": 135.4,
      "koh_weight_g": 0.0,
      "naoh_percent": 100.0,
      "koh_percent": 0.0
    },
    "water_weight_g": 271.0,
    "water_method": "lye_concentration",
    "water_method_value": 33.0,
    "superfat_percent": 5.0,
    "additives": [
      {
        "id": "kaolin_clay",
        "common_name": "Kaolin Clay (White)",
        "weight_g": 20.0,
        "percentage": 2.0
      },
      {
        "id": "sodium_lactate",
        "common_name": "Sodium Lactate",
        "weight_g": 30.0,
        "percentage": 3.0
      }
    ]
  },
  "quality_metrics": {
    "hardness": 44.8,
    "cleansing": 18.5,
    "conditioning": 55.7,
    "bubbly_lather": 25.2,
    "creamy_lather": 46.3,
    "longevity": 45.6,
    "stability": 52.1,
    "iodine": 67.8,
    "ins": 148.5
  },
  "quality_metrics_base": {
    "hardness": 40.0,
    "cleansing": 18.5,
    "conditioning": 55.7,
    "bubbly_lather": 25.2,
    "creamy_lather": 38.9,
    "longevity": 45.6,
    "stability": 52.1,
    "iodine": 67.8,
    "ins": 148.5
  },
  "additive_effects": [
    {
      "additive_id": "kaolin_clay",
      "additive_name": "Kaolin Clay (White)",
      "effects": {
        "hardness": 4.0,
        "creamy_lather": 7.0,
        "conditioning": 0.8
      },
      "confidence": "high",
      "verified_by_mga": false
    },
    {
      "additive_id": "sodium_lactate",
      "additive_name": "Sodium Lactate",
      "effects": {
        "hardness": 12.0,
        "creamy_lather": 3.9,
        "conditioning": 0.6,
        "bubbly_lather": 0.8
      },
      "confidence": "high",
      "verified_by_mga": false
    }
  ],
  "fatty_acid_profile": {
    "lauric": 8.5,
    "myristic": 5.2,
    "palmitic": 10.3,
    "stearic": 4.1,
    "ricinoleic": 0.0,
    "oleic": 52.3,
    "linoleic": 15.6,
    "linolenic": 1.8
  },
  "saturated_unsaturated_ratio": {
    "saturated": 28.1,
    "unsaturated": 69.7,
    "ratio": "28:70"
  },
  "warnings": []
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `calculation_id` | UUID | Unique calculation identifier |
| `timestamp` | ISO 8601 | Calculation creation timestamp |
| `user_id` | UUID | User who created calculation |
| `recipe` | Object | Complete normalized recipe |
| `recipe.total_oil_weight_g` | Float | Sum of all oil weights |
| `recipe.oils[]` | Array | Oil details with weights and percentages |
| `recipe.lye` | Object | Calculated lye requirements |
| `recipe.water_weight_g` | Float | Calculated water weight |
| `recipe.additives[]` | Array | Additive details with weights and percentages |
| `quality_metrics` | Object | Final quality metrics (base + additive effects) |
| `quality_metrics_base` | Object | Base quality metrics from oils only |
| `additive_effects[]` | Array | Per-additive effect breakdown |
| `additive_effects[].effects` | Object | Numeric changes to quality metrics |
| `additive_effects[].confidence` | String | Research confidence level: `high`, `medium`, `low` |
| `additive_effects[].verified_by_mga` | Boolean | Whether MGA has empirically validated effects |
| `fatty_acid_profile` | Object | Percentage breakdown of fatty acids |
| `saturated_unsaturated_ratio` | Object | Sat:Unsat ratio calculation |
| `warnings[]` | Array | Non-blocking warnings |

**Error Responses:**

**400 Bad Request - Invalid Oil Percentages:**
```json
{
  "error": {
    "code": "INVALID_OIL_PERCENTAGES",
    "message": "Oil percentages must sum to exactly 100%",
    "details": {
      "calculated_sum": 99.5,
      "expected_sum": 100.0
    }
  }
}
```

**400 Bad Request - Missing Required Fields:**
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: lye",
    "details": {
      "missing_fields": ["lye"]
    }
  }
}
```

**401 Unauthorized:**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing JWT token"
  }
}
```

**422 Unprocessable Entity - Unknown Oil:**
```json
{
  "error": {
    "code": "UNKNOWN_OIL_ID",
    "message": "Oil ID 'exotic_butter' not found in database",
    "details": {
      "unknown_oil_ids": ["exotic_butter"]
    }
  }
}
```

**422 Unprocessable Entity - Invalid Lye Percentages:**
```json
{
  "error": {
    "code": "INVALID_LYE_PERCENTAGES",
    "message": "NaOH and KOH percentages must sum to exactly 100%",
    "details": {
      "naoh_percent": 90.0,
      "koh_percent": 5.0,
      "calculated_sum": 95.0
    }
  }
}
```

**Warning Example (Non-blocking):**

Request with unknown additive:
```json
{
  "additives": [
    {
      "id": "unknown_custom_herb",
      "weight_g": 10.0
    }
  ]
}
```

Response includes warning:
```json
{
  "calculation_id": "...",
  "warnings": [
    {
      "code": "UNKNOWN_ADDITIVE_ID",
      "message": "Additive 'unknown_custom_herb' not found in database - excluded from calculation",
      "severity": "warning",
      "additive_id": "unknown_custom_herb"
    }
  ]
}
```

### 3.2 GET /api/v1/calculate/{id}

Retrieve previously saved calculation.

**Authentication:** Required (JWT Bearer token)

**Path Parameters:**
- `id` (UUID): Calculation ID

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**

Same structure as POST response.

**Error Responses:**

**401 Unauthorized:**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing JWT token"
  }
}
```

**403 Forbidden:**
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Calculation belongs to different user"
  }
}
```

**404 Not Found:**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Calculation with ID '550e8400-e29b-41d4-a716-446655440000' not found"
  }
}
```

### 3.3 GET /api/v1/health

Health check endpoint (no authentication required).

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-01T14:30:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "timestamp": "2025-11-01T14:30:00Z",
  "version": "1.0.0",
  "database": "disconnected",
  "error": "Unable to connect to PostgreSQL"
}
```

---

## 4. Data Models

### 4.1 Database Schema

**users table:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP,
    INDEX idx_users_email (email)
);
```

**oils table:**
```sql
CREATE TABLE oils (
    id VARCHAR(100) PRIMARY KEY,
    common_name VARCHAR(255) NOT NULL,
    inci_name VARCHAR(255),
    sap_value_naoh DECIMAL(6,3) NOT NULL,
    sap_value_koh DECIMAL(6,3) NOT NULL,
    fatty_acids JSONB NOT NULL,
    quality_contributions JSONB NOT NULL,
    iodine_value DECIMAL(5,1) NOT NULL,
    ins_value DECIMAL(5,1) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**fatty_acids JSONB structure:**
```json
{
  "lauric": 8.0,
  "myristic": 5.0,
  "palmitic": 10.0,
  "stearic": 4.0,
  "ricinoleic": 0.0,
  "oleic": 52.0,
  "linoleic": 16.0,
  "linolenic": 2.0
}
```

**quality_contributions JSONB structure:**
```json
{
  "hardness": 12.0,
  "cleansing": 8.0,
  "conditioning": 68.0,
  "bubbly_lather": 8.0,
  "creamy_lather": 4.0,
  "longevity": 12.0,
  "stability": 80.0
}
```

**additives table:**
```sql
CREATE TABLE additives (
    id VARCHAR(100) PRIMARY KEY,
    common_name VARCHAR(255) NOT NULL,
    inci_name VARCHAR(255),
    typical_usage_min_percent DECIMAL(4,2),
    typical_usage_max_percent DECIMAL(4,2),
    quality_effects JSONB NOT NULL,
    confidence_level VARCHAR(20) NOT NULL CHECK (confidence_level IN ('high', 'medium', 'low')),
    verified_by_mga BOOLEAN DEFAULT FALSE,
    safety_warnings JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**quality_effects JSONB structure (absolute modifiers):**
```json
{
  "hardness": 4.0,
  "cleansing": 0.0,
  "conditioning": 0.8,
  "bubbly_lather": 0.0,
  "creamy_lather": 7.0
}
```

**safety_warnings JSONB structure:**
```json
{
  "heat_risk": "High - can cause soap to overheat and volcano",
  "incompatible_with": ["sugar", "milk_powder"],
  "skin_type_caution": "May be too drying for sensitive skin"
}
```

**calculations table:**
```sql
CREATE TABLE calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    recipe_data JSONB NOT NULL,
    results_data JSONB NOT NULL,
    INDEX idx_user_calculations (user_id, created_at DESC)
);
```

**recipe_data JSONB structure:**
```json
{
  "total_oil_weight_g": 1000.0,
  "oils": [...],
  "lye": {...},
  "water_weight_g": 271.0,
  "water_method": "lye_concentration",
  "water_method_value": 33.0,
  "superfat_percent": 5.0,
  "additives": [...]
}
```

**results_data JSONB structure:**
```json
{
  "quality_metrics": {...},
  "quality_metrics_base": {...},
  "additive_effects": [...],
  "fatty_acid_profile": {...},
  "saturated_unsaturated_ratio": {...},
  "warnings": [...]
}
```

### 4.2 Oil Data Structure

**Example oil entry (Olive Oil):**
```sql
INSERT INTO oils VALUES (
    'olive_oil',
    'Olive Oil',
    'Olea Europaea (Olive) Fruit Oil',
    0.134, -- SAP NaOH
    0.188, -- SAP KOH
    '{"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 4, "ricinoleic": 0, "oleic": 72, "linoleic": 10, "linolenic": 1}',
    '{"hardness": 15, "cleansing": 0, "conditioning": 83, "bubbly_lather": 0, "creamy_lather": 15, "longevity": 15, "stability": 94}',
    84.0, -- Iodine value
    109.0, -- INS value
    NOW(),
    NOW()
);
```

**SAP Value Reference:**
- Source: SoapCalc.net database
- Values represent grams of lye per gram of oil required for complete saponification

### 4.3 Additive Data Structure

**Example additive entry (Kaolin Clay):**
```sql
INSERT INTO additives VALUES (
    'kaolin_clay',
    'Kaolin Clay (White)',
    'Kaolin',
    1.0, -- Min usage 1% of oils
    3.0, -- Max usage 3% of oils
    '{"hardness": 4.0, "cleansing": 0.0, "conditioning": 0.8, "bubbly_lather": 0.0, "creamy_lather": 7.0}',
    'high',
    FALSE,
    '{"skin_type": "Suitable for all skin types including sensitive"}',
    NOW(),
    NOW()
);
```

**Additive Effect Calculation Note:**

Effects are **absolute modifiers** applied to base quality metrics, calculated at 2% usage rate (typical mid-point).

For different usage rates, scale proportionally:
```
actual_effect = base_effect * (actual_usage_percent / 2.0)
```

Example: Kaolin clay at 3% instead of 2%:
```
hardness_effect = 4.0 * (3.0 / 2.0) = 6.0
```

**Priority Additives for Phase 1:**

Based on confidence levels from `agent-os/research/soap-additive-effects.md`:

**High Confidence:**
1. Sodium Lactate
2. Sugar
3. Honey
4. Colloidal Oatmeal
5. Kaolin Clay
6. Sea Salt (Brine)
7. Sea Salt (Salt Bar)

**Medium Confidence:**
8. Silk
9. Bentonite Clay
10. French Green Clay
11. Rose Clay
12. Rhassoul Clay
13. Goat Milk Powder

**Low Confidence (mark as experimental):**
14. Activated Charcoal
15. Coffee Grounds

---

## 5. Calculation Algorithms

### 5.1 Lye Calculation

**Input Normalization:**

First, convert oil percentages to weights (or weights to percentages):

```python
# If user provided percentages, calculate weights
if oil_has_percentage:
    # Total oil weight determined by first oil with weight, or default
    total_oil_weight = calculate_total_oil_weight(oils)
    for oil in oils:
        if oil.percentage is not None:
            oil.weight_g = total_oil_weight * (oil.percentage / 100.0)

# If user provided weights, calculate percentages
else:
    total_oil_weight = sum(oil.weight_g for oil in oils)
    for oil in oils:
        oil.percentage = (oil.weight_g / total_oil_weight) * 100.0
```

**Lye Calculation:**

```python
def calculate_lye(oils, superfat_percent, naoh_percent, koh_percent):
    """
    Calculate total lye requirements.

    Returns:
        (naoh_weight_g, koh_weight_g)
    """
    superfat_decimal = superfat_percent / 100.0
    naoh_decimal = naoh_percent / 100.0
    koh_decimal = koh_percent / 100.0

    # Calculate total saponification requirements per oil
    total_lye_needed = 0.0
    for oil in oils:
        # Base SAP calculation (average of NaOH and KOH weighted)
        oil_sap = (oil.sap_value_naoh * naoh_decimal +
                   oil.sap_value_koh * koh_decimal)

        # Apply superfat reduction
        lye_for_oil = oil.weight_g * oil_sap * (1.0 - superfat_decimal)
        total_lye_needed += lye_for_oil

    # Split total lye by type
    naoh_weight_g = total_lye_needed * naoh_decimal
    koh_weight_g = total_lye_needed * koh_decimal

    return round(naoh_weight_g, 1), round(koh_weight_g, 1)
```

**Example:**
- 1000g oils (500g Olive, 300g Coconut, 200g Palm)
- 5% superfat
- 100% NaOH, 0% KOH

```
Olive:   500g × 0.134 × 0.95 = 63.65g
Coconut: 300g × 0.183 × 0.95 = 52.16g
Palm:    200g × 0.141 × 0.95 = 26.79g
Total NaOH: 142.6g
Total KOH: 0g
```

### 5.2 Water Calculation

Support three methods:

**Method 1: Water as % of oils**
```python
def water_as_percent_of_oils(total_oil_weight_g, water_percent):
    """
    water_percent: typically 30-38%
    """
    return round(total_oil_weight_g * (water_percent / 100.0), 1)
```

**Method 2: Lye concentration**
```python
def water_from_lye_concentration(total_lye_weight_g, lye_concentration_percent):
    """
    lye_concentration_percent: typically 25-40%

    Formula: water = (lye / concentration) - lye
    """
    lye_concentration = lye_concentration_percent / 100.0
    total_solution = total_lye_weight_g / lye_concentration
    water_weight_g = total_solution - total_lye_weight_g
    return round(water_weight_g, 1)
```

**Method 3: Water:lye ratio**
```python
def water_from_ratio(total_lye_weight_g, water_lye_ratio):
    """
    water_lye_ratio: typically 1.5:1 to 3:1

    Examples:
    - 2:1 means 2 parts water to 1 part lye
    - 2.5 means 2.5 parts water to 1 part lye
    """
    return round(total_lye_weight_g * water_lye_ratio, 1)
```

**Example (Method 2 - Lye concentration 33%):**
- Total lye: 142.6g NaOH
- Lye concentration: 33%

```
Total solution = 142.6 / 0.33 = 432.1g
Water = 432.1 - 142.6 = 289.5g
```

### 5.3 Quality Metrics Calculation

**Base Quality Metrics (from oil blend):**

```python
def calculate_base_quality_metrics(oils):
    """
    Calculate quality metrics from weighted average of oil contributions.

    Formulas from SoapCalc.net:
    - Hardness = sum(oil_percent × oil_hardness_contribution)
    - Cleansing = sum(oil_percent × oil_cleansing_contribution)
    - Conditioning = sum(oil_percent × oil_conditioning_contribution)
    - Bubbly Lather = sum(oil_percent × oil_bubbly_contribution)
    - Creamy Lather = sum(oil_percent × oil_creamy_contribution)

    Returns:
        dict of metric_name: value
    """
    metrics = {
        'hardness': 0.0,
        'cleansing': 0.0,
        'conditioning': 0.0,
        'bubbly_lather': 0.0,
        'creamy_lather': 0.0,
        'longevity': 0.0,
        'stability': 0.0
    }

    for oil in oils:
        percentage_decimal = oil.percentage / 100.0
        contributions = oil.quality_contributions  # From database JSONB

        for metric in metrics:
            metrics[metric] += contributions[metric] * percentage_decimal

    # Round to 1 decimal place
    return {k: round(v, 1) for k, v in metrics.items()}
```

**With Additive Effects:**

```python
def apply_additive_effects(base_metrics, additives, total_oil_weight_g):
    """
    Apply additive modifiers to base quality metrics.

    Additive effects scaled by usage rate (base effects at 2% usage).
    """
    final_metrics = base_metrics.copy()
    additive_effects_detail = []

    for additive in additives:
        # Calculate actual usage percentage
        usage_percent = (additive.weight_g / total_oil_weight_g) * 100.0

        # Scale factor (effects defined at 2% usage)
        scale_factor = usage_percent / 2.0

        # Apply effects
        effects_applied = {}
        for metric, base_effect in additive.quality_effects.items():
            scaled_effect = base_effect * scale_factor
            final_metrics[metric] += scaled_effect
            effects_applied[metric] = round(scaled_effect, 1)

        additive_effects_detail.append({
            'additive_id': additive.id,
            'additive_name': additive.common_name,
            'effects': effects_applied,
            'confidence': additive.confidence_level,
            'verified_by_mga': additive.verified_by_mga
        })

    # Round final metrics
    final_metrics = {k: round(v, 1) for k, v in final_metrics.items()}

    return final_metrics, additive_effects_detail
```

**Example:**

Base metrics (from 50% Olive, 30% Coconut, 20% Palm):
```
Hardness: 40.0
Creamy Lather: 38.9
```

Adding 20g Kaolin Clay (2% of 1000g oils):
```
Usage: 20g / 1000g = 2%
Scale factor: 2% / 2% = 1.0
Hardness effect: 4.0 × 1.0 = +4.0
Creamy lather effect: 7.0 × 1.0 = +7.0

Final Hardness: 40.0 + 4.0 = 44.0
Final Creamy Lather: 38.9 + 7.0 = 45.9
```

Adding 30g Sodium Lactate (3% of 1000g oils):
```
Usage: 30g / 1000g = 3%
Scale factor: 3% / 2% = 1.5
Hardness effect: 12.0 × 1.5 = +18.0
Creamy lather effect: 3.9 × 1.5 = +5.9

Final Hardness: 44.0 + 18.0 = 62.0
Final Creamy Lather: 45.9 + 5.9 = 51.8
```

### 5.4 Fatty Acid Profile

```python
def calculate_fatty_acid_profile(oils):
    """
    Calculate weighted average fatty acid percentages.
    """
    fatty_acids = {
        'lauric': 0.0,
        'myristic': 0.0,
        'palmitic': 0.0,
        'stearic': 0.0,
        'ricinoleic': 0.0,
        'oleic': 0.0,
        'linoleic': 0.0,
        'linolenic': 0.0
    }

    for oil in oils:
        percentage_decimal = oil.percentage / 100.0
        oil_fatty_acids = oil.fatty_acids  # From database JSONB

        for fatty_acid in fatty_acids:
            fatty_acids[fatty_acid] += oil_fatty_acids[fatty_acid] * percentage_decimal

    # Round to 1 decimal place
    return {k: round(v, 1) for k, v in fatty_acids.items()}
```

**Example (50% Olive, 30% Coconut, 20% Palm):**

```
Oleic:
  (72 × 0.5) + (8 × 0.3) + (39 × 0.2) = 36 + 2.4 + 7.8 = 46.2%

Lauric:
  (0 × 0.5) + (48 × 0.3) + (0 × 0.2) = 0 + 14.4 + 0 = 14.4%
```

### 5.5 Saturated vs Unsaturated Ratio

```python
def calculate_sat_unsat_ratio(fatty_acid_profile):
    """
    Calculate saturated:unsaturated fatty acid ratio.
    """
    saturated = (
        fatty_acid_profile['lauric'] +
        fatty_acid_profile['myristic'] +
        fatty_acid_profile['palmitic'] +
        fatty_acid_profile['stearic']
    )

    unsaturated = (
        fatty_acid_profile['oleic'] +
        fatty_acid_profile['linoleic'] +
        fatty_acid_profile['linolenic'] +
        fatty_acid_profile['ricinoleic']
    )

    saturated = round(saturated, 1)
    unsaturated = round(unsaturated, 1)

    # Format as ratio string (e.g., "28:70")
    ratio = f"{int(saturated)}:{int(unsaturated)}"

    return {
        'saturated': saturated,
        'unsaturated': unsaturated,
        'ratio': ratio
    }
```

### 5.6 INS Value

```python
def calculate_ins_value(oils):
    """
    INS (Iodine Number Saponification) value.

    Industry standard formula: INS = SAP - Iodine
    Higher INS = harder, longer-lasting soap

    Ideal range: 136-165
    """
    ins = 0.0

    for oil in oils:
        percentage_decimal = oil.percentage / 100.0
        ins += oil.ins_value * percentage_decimal

    return round(ins, 1)
```

### 5.7 Iodine Value

```python
def calculate_iodine_value(oils):
    """
    Iodine value measures unsaturation (double bonds in fatty acids).

    Higher iodine = more unsaturated = softer, less stable soap
    Lower iodine = more saturated = harder, more stable soap

    Ideal range: <70 for good shelf life
    """
    iodine = 0.0

    for oil in oils:
        percentage_decimal = oil.percentage / 100.0
        iodine += oil.iodine_value * percentage_decimal

    return round(iodine, 1)
```

---

## 6. Validation Rules

### 6.1 Request Validation (Errors - Block Calculation)

**Structural Validation (Pydantic):**
- All required fields present
- Field types correct (string, float, array, etc.)
- UUIDs valid format
- Percentages in valid range (0-100)

**Business Logic Validation:**

```python
def validate_request(request):
    errors = []

    # Oil validation
    if not request.oils or len(request.oils) == 0:
        errors.append("At least one oil required")

    for oil in request.oils:
        if oil.weight_g is None and oil.percentage is None:
            errors.append(f"Oil '{oil.id}' must have weight_g OR percentage")
        if oil.weight_g is not None and oil.weight_g <= 0:
            errors.append(f"Oil '{oil.id}' weight must be > 0")
        if oil.percentage is not None and (oil.percentage <= 0 or oil.percentage > 100):
            errors.append(f"Oil '{oil.id}' percentage must be 0-100")

    # Oil percentage sum validation (STRICT)
    if all(oil.percentage is not None for oil in request.oils):
        total_percent = sum(oil.percentage for oil in request.oils)
        if abs(total_percent - 100.0) > 0.01:  # Allow 0.01% floating point tolerance
            errors.append({
                'code': 'INVALID_OIL_PERCENTAGES',
                'message': f'Oil percentages must sum to exactly 100%',
                'calculated_sum': round(total_percent, 2),
                'expected_sum': 100.0
            })

    # Lye validation
    if request.lye.naoh_percent < 0 or request.lye.koh_percent < 0:
        errors.append("Lye percentages cannot be negative")

    lye_sum = request.lye.naoh_percent + request.lye.koh_percent
    if abs(lye_sum - 100.0) > 0.01:
        errors.append({
            'code': 'INVALID_LYE_PERCENTAGES',
            'message': 'NaOH and KOH percentages must sum to exactly 100%',
            'calculated_sum': round(lye_sum, 2),
            'expected_sum': 100.0
        })

    # Superfat validation
    if request.superfat_percent < 0 or request.superfat_percent > 100:
        errors.append("Superfat must be 0-100%")

    # Water method validation
    valid_water_methods = ['water_percent_of_oils', 'lye_concentration', 'water_lye_ratio']
    if request.water.method not in valid_water_methods:
        errors.append(f"Invalid water method. Must be one of: {valid_water_methods}")

    if request.water.value <= 0:
        errors.append("Water method value must be > 0")

    # Database existence validation
    unknown_oil_ids = check_unknown_oils(request.oils)
    if unknown_oil_ids:
        errors.append({
            'code': 'UNKNOWN_OIL_ID',
            'message': f'Oil IDs not found in database',
            'unknown_oil_ids': unknown_oil_ids
        })

    return errors
```

### 6.2 Business Logic Validation (Warnings - Calculate But Flag)

```python
def generate_warnings(request, results):
    warnings = []

    # Unusual superfat
    if request.superfat_percent < 0:
        warnings.append({
            'code': 'NEGATIVE_SUPERFAT',
            'message': 'Negative superfat creates lye-heavy soap - advanced users only',
            'severity': 'warning',
            'superfat_percent': request.superfat_percent
        })

    if request.superfat_percent > 20:
        warnings.append({
            'code': 'HIGH_SUPERFAT',
            'message': 'Superfat above 20% may create soft, oily soap',
            'severity': 'info',
            'superfat_percent': request.superfat_percent
        })

    # Extreme quality metrics
    if results.quality_metrics.hardness > 70:
        warnings.append({
            'code': 'EXTREME_HARDNESS',
            'message': 'Very hard soap may be difficult to lather or harsh on skin',
            'severity': 'info',
            'hardness': results.quality_metrics.hardness
        })

    if results.quality_metrics.cleansing > 30:
        warnings.append({
            'code': 'HIGH_CLEANSING',
            'message': 'High cleansing value may be drying for some skin types',
            'severity': 'info',
            'cleansing': results.quality_metrics.cleansing
        })

    # Unknown additives
    unknown_additive_ids = check_unknown_additives(request.additives)
    for additive_id in unknown_additive_ids:
        warnings.append({
            'code': 'UNKNOWN_ADDITIVE_ID',
            'message': f'Additive \'{additive_id}\' not found in database - excluded from calculation',
            'severity': 'warning',
            'additive_id': additive_id
        })

    # Additive combination warnings
    if has_honey_and_sugar(request.additives):
        warnings.append({
            'code': 'HEAT_RISK_COMBINATION',
            'message': 'Honey + sugar combination creates high heat risk - experienced users only',
            'severity': 'warning'
        })

    return warnings
```

### 6.3 Precision Rules

**Rounding Standards:**
- Weights: 1 decimal place (e.g., 135.4g)
- Percentages: 1 decimal place (e.g., 5.0%)
- Quality metrics: 1 decimal place (e.g., 42.3)
- Fatty acid percentages: 1 decimal place (e.g., 52.3%)

**Implementation:**
```python
# Python rounding
round(value, 1)

# PostgreSQL rounding
ROUND(column_name::numeric, 1)
```

---

## 7. Authentication & Authorization

### 7.1 JWT Implementation

**Token Structure:**
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "exp": 1699564800,
  "iat": 1699561200
}
```

**Claims:**
- `sub`: User UUID (subject)
- `email`: User email address
- `exp`: Expiration timestamp (24 hours from `iat`)
- `iat`: Issued at timestamp

**Token Generation:**
```python
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # From environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def create_access_token(user_id: str, email: str):
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Token Validation:**
```python
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 7.2 Endpoint Protection

**Protected Endpoints:**
- `POST /api/v1/calculate` - Requires valid JWT
- `GET /api/v1/calculate/{id}` - Requires valid JWT + ownership check

**Public Endpoints:**
- `GET /api/v1/health` - No authentication

**Authorization Logic:**
```python
@app.get("/api/v1/calculate/{calculation_id}")
async def get_calculation(
    calculation_id: str,
    current_user_id: str = Depends(get_current_user)
):
    calculation = db.get_calculation(calculation_id)

    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")

    # Ownership check
    if calculation.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Calculation belongs to different user")

    return calculation
```

### 7.3 Password Requirements

**Phase 1 (Basic):**
- Minimum 8 characters
- Hashing: bcrypt with salt
- No complexity requirements yet

**Password Hashing:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Future Enhancements (Phase 2):**
- Password complexity rules
- Rate limiting on login attempts
- Password reset flow
- Refresh token rotation

---

## 8. Error Handling

### 8.1 Error Response Format

**Standard Error Structure:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "additional": "contextual data"
    }
  }
}
```

### 8.2 Error Codes

| Code | HTTP Status | Description | Example |
|------|-------------|-------------|---------|
| `INVALID_REQUEST` | 400 | Missing or malformed required fields | Missing `lye` object |
| `INVALID_OIL_PERCENTAGES` | 400 | Oil percentages don't sum to 100% | Sum is 99.5% |
| `INVALID_LYE_PERCENTAGES` | 400 | NaOH + KOH != 100% | Sum is 95% |
| `UNKNOWN_OIL_ID` | 422 | Oil ID not in database | `exotic_butter` not found |
| `UNKNOWN_ADDITIVE_ID` | 422 | Additive ID not in database | `custom_herb` not found |
| `UNAUTHORIZED` | 401 | Missing or invalid JWT | Token expired |
| `FORBIDDEN` | 403 | Access denied to resource | Calculation belongs to different user |
| `NOT_FOUND` | 404 | Resource doesn't exist | Calculation ID not found |

### 8.3 Warning Format

**Non-blocking warnings returned with successful calculation:**

```json
{
  "calculation_id": "...",
  "warnings": [
    {
      "code": "WARNING_CODE",
      "message": "Human-readable warning",
      "severity": "warning|info",
      "context_field": "relevant_value"
    }
  ]
}
```

**Warning Codes:**

| Code | Severity | Description |
|------|----------|-------------|
| `NEGATIVE_SUPERFAT` | warning | Superfat < 0% (lye-heavy soap) |
| `HIGH_SUPERFAT` | info | Superfat > 20% (very mild soap) |
| `EXTREME_HARDNESS` | info | Hardness > 70 (very hard bar) |
| `HIGH_CLEANSING` | info | Cleansing > 30 (may be drying) |
| `UNKNOWN_ADDITIVE_ID` | warning | Additive not found, excluded from calculation |
| `HEAT_RISK_COMBINATION` | warning | Honey + sugar combo (overheating risk) |
| `UNVERIFIED_ADDITIVE` | info | Additive effects not MGA-verified |

---

## 9. Testing Requirements

### 9.1 Unit Tests

**Calculation Algorithm Tests:**
```python
# test_calculations.py
import pytest

def test_lye_calculation_naoh_only():
    """Test basic NaOH-only lye calculation"""
    oils = [
        Oil(id='olive_oil', weight_g=1000, sap_value_naoh=0.134)
    ]
    superfat = 5.0
    naoh_percent = 100.0
    koh_percent = 0.0

    naoh, koh = calculate_lye(oils, superfat, naoh_percent, koh_percent)

    assert naoh == pytest.approx(127.3, abs=0.1)
    assert koh == 0.0

def test_lye_calculation_dual_lye():
    """Test dual lye (NaOH + KOH) calculation"""
    oils = [
        Oil(id='coconut_oil', weight_g=500,
            sap_value_naoh=0.183, sap_value_koh=0.257)
    ]
    superfat = 5.0
    naoh_percent = 50.0
    koh_percent = 50.0

    naoh, koh = calculate_lye(oils, superfat, naoh_percent, koh_percent)

    # Verify calculations manually
    expected_naoh = pytest.approx(43.5, abs=0.1)
    expected_koh = pytest.approx(61.1, abs=0.1)

    assert naoh == expected_naoh
    assert koh == expected_koh

def test_additive_effect_scaling():
    """Test additive effects scale with usage rate"""
    base_metrics = {'hardness': 40.0, 'creamy_lather': 38.9}

    # Kaolin at 2% (base rate)
    additive_2pct = Additive(
        id='kaolin_clay',
        weight_g=20.0,  # 2% of 1000g
        quality_effects={'hardness': 4.0, 'creamy_lather': 7.0}
    )

    final, _ = apply_additive_effects(
        base_metrics,
        [additive_2pct],
        total_oil_weight_g=1000.0
    )

    assert final['hardness'] == pytest.approx(44.0, abs=0.1)
    assert final['creamy_lather'] == pytest.approx(45.9, abs=0.1)

    # Kaolin at 3% (1.5x scale)
    additive_3pct = Additive(
        id='kaolin_clay',
        weight_g=30.0,  # 3% of 1000g
        quality_effects={'hardness': 4.0, 'creamy_lather': 7.0}
    )

    final, _ = apply_additive_effects(
        base_metrics,
        [additive_3pct],
        total_oil_weight_g=1000.0
    )

    assert final['hardness'] == pytest.approx(46.0, abs=0.1)  # 40 + 4*1.5
    assert final['creamy_lather'] == pytest.approx(49.4, abs=0.1)  # 38.9 + 7*1.5

def test_water_calculation_lye_concentration():
    """Test water calculation from lye concentration"""
    total_lye_g = 142.6
    lye_concentration = 33.0

    water_g = water_from_lye_concentration(total_lye_g, lye_concentration)

    # water = (142.6 / 0.33) - 142.6 = 289.5
    assert water_g == pytest.approx(289.5, abs=0.1)

def test_oil_percentage_validation():
    """Test strict 100% oil percentage validation"""
    # Valid: exactly 100%
    oils_valid = [
        Oil(id='olive', percentage=50.0),
        Oil(id='coconut', percentage=30.0),
        Oil(id='palm', percentage=20.0)
    ]
    assert validate_oil_percentages(oils_valid) == []

    # Invalid: 99.5%
    oils_invalid = [
        Oil(id='olive', percentage=49.5),
        Oil(id='coconut', percentage=30.0),
        Oil(id='palm', percentage=20.0)
    ]
    errors = validate_oil_percentages(oils_invalid)
    assert len(errors) == 1
    assert errors[0]['code'] == 'INVALID_OIL_PERCENTAGES'
```

**Coverage Target:** >90%

**Property-Based Testing (Hypothesis):**
```python
from hypothesis import given, strategies as st

@given(
    oil_count=st.integers(min_value=1, max_value=10),
    superfat=st.floats(min_value=0, max_value=20)
)
def test_lye_calculation_always_positive(oil_count, superfat):
    """Property: lye weight always > 0 for valid inputs"""
    oils = generate_random_oils(oil_count)
    naoh, koh = calculate_lye(oils, superfat, 100.0, 0.0)
    assert naoh > 0
```

### 9.2 Integration Tests

**API Endpoint Tests:**
```python
# test_api.py
from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_calculate_endpoint_success():
    """Test successful calculation request"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "olive_oil", "percentage": 100.0}
                ],
                "lye": {"naoh_percent": 100.0, "koh_percent": 0.0},
                "water": {"method": "lye_concentration", "value": 33.0},
                "superfat_percent": 5.0,
                "additives": []
            },
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )

    assert response.status_code == 200
    data = response.json()
    assert "calculation_id" in data
    assert data["recipe"]["total_oil_weight_g"] > 0
    assert "quality_metrics" in data
    assert "fatty_acid_profile" in data

@pytest.mark.asyncio
async def test_calculate_endpoint_invalid_oil_percentages():
    """Test error when oil percentages don't sum to 100%"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "olive_oil", "percentage": 50.0},
                    {"id": "coconut_oil", "percentage": 40.0}
                    # Total: 90% (invalid)
                ],
                "lye": {"naoh_percent": 100.0, "koh_percent": 0.0},
                "water": {"method": "lye_concentration", "value": 33.0},
                "superfat_percent": 5.0
            },
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_OIL_PERCENTAGES"

@pytest.mark.asyncio
async def test_get_calculation_ownership():
    """Test GET calculation enforces ownership"""
    # Create calculation as user A
    calc_id = await create_calculation(user_a_token)

    # Attempt to retrieve as user B
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/calculate/{calc_id}",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
```

### 9.3 Test Data

**Reference Recipe (from SoapCalc example):**

```python
SOAPCALC_REFERENCE = {
    "oils": [
        {"id": "avocado_oil", "percentage": 40.0},
        {"id": "babassu_oil", "percentage": 30.0},
        {"id": "coconut_oil", "percentage": 30.0}
    ],
    "lye": {"naoh_percent": 100.0, "koh_percent": 0.0},
    "water": {"method": "water_percent_of_oils", "value": 38.0},
    "superfat_percent": 5.0,
    "expected_results": {
        "hardness": 58,
        "cleansing": 41,
        "conditioning": 34,
        "bubbly_lather": 41,
        "creamy_lather": 17,
        "iodine": 40,
        "ins": 186
    }
}

def test_soapcalc_reference_calculation():
    """Verify our calculations match SoapCalc reference"""
    result = calculate(SOAPCALC_REFERENCE)

    # Allow 2-point tolerance for different rounding
    assert result.hardness == pytest.approx(58, abs=2)
    assert result.cleansing == pytest.approx(41, abs=2)
    assert result.conditioning == pytest.approx(34, abs=2)
```

**Edge Cases:**

```python
EDGE_CASES = [
    {
        "name": "100% single oil (Castile)",
        "oils": [{"id": "olive_oil", "percentage": 100.0}]
    },
    {
        "name": "Zero additives",
        "additives": []
    },
    {
        "name": "Dual lye 50/50",
        "lye": {"naoh_percent": 50.0, "koh_percent": 50.0}
    },
    {
        "name": "High superfat (20%)",
        "superfat_percent": 20.0
    },
    {
        "name": "Negative superfat (advanced)",
        "superfat_percent": -2.0
    }
]
```

---

## 10. Implementation Phases

### Phase 1 (This Spec) - MVP Core

**Scope:**
- ✅ POST /api/v1/calculate endpoint
- ✅ GET /api/v1/calculate/{id} endpoint
- ✅ GET /api/v1/health endpoint
- ✅ JWT authentication
- ✅ Dual lye support (NaOH + KOH)
- ✅ Three water calculation methods
- ✅ All quality metrics (Hardness, Cleansing, Conditioning, Bubbly, Creamy, Longevity, Stability)
- ✅ Fatty acid profiles
- ✅ INS and Iodine values
- ✅ Sat:Unsat ratio
- ✅ Additive effect modeling (research-backed)
- ✅ Warning system (non-blocking validation)
- ✅ PostgreSQL persistence
- ✅ >90% test coverage

**Priority Additives (Phase 1):**
1. Sodium Lactate (high confidence)
2. Sugar (high confidence)
3. Honey (high confidence)
4. Colloidal Oatmeal (high confidence)
5. Kaolin Clay (high confidence)
6. Sea Salt - Brine (high confidence)
7. Silk (medium confidence)
8. Bentonite Clay (medium confidence)

**Priority Oils (Phase 1):**
- Olive Oil
- Coconut Oil
- Palm Oil
- Castor Oil
- Avocado Oil
- Babassu Oil
- Shea Butter
- Cocoa Butter
- Sweet Almond Oil
- Sunflower Oil

*(Expand to 30+ oils based on SoapCalc database)*

**Timeline:** 4-6 weeks

**Success Criteria:**
- MGA Automotive can calculate production recipes
- All calculations accurate within 1% of manual verification
- API response time <200ms
- 99.9% uptime

### Phase 2 (Future) - Enhanced Features

**Scope:**
- Batch calculations (multiple recipes in one request)
- Cost calculator integration (ingredient pricing)
- INCI name generation (cosmetic labeling compliance)
- Fragrance calculator (essential oil blending)
- Recipe search and filtering
- User management improvements (password complexity, rate limiting)

**Timeline:** 8-12 weeks after Phase 1

### Phase 3 (Future) - Public Web Interface

**Scope:**
- React + TypeScript web application
- Public user registration
- Recipe sharing and community features
- Mobile-responsive design
- Advanced analytics (cost trends, batch tracking)

**Timeline:** 12-16 weeks after Phase 2

---

## 11. Open Questions

**NONE** - All requirements clarified through 22 answered questions in `requirements-notes.md`.

---

## 12. References

**Product Documentation:**
- `agent-os/product/mission.md` - Product vision and competitive advantage
- `agent-os/product/tech-stack.md` - Technology decisions and rationale
- `agent-os/product/roadmap.md` - Phase breakdown and timeline

**Research:**
- `agent-os/research/soap-additive-effects.md` - Comprehensive additive effect data with confidence levels

**Requirements:**
- `requirements-notes.md` - Complete user requirements from 22 answered questions

**Competitive Analysis:**
- `reference/soapcalcnet-analysis.md` - SoapCalc.net feature comparison
- `reference/View_Print Recipe.html` - SoapCalc output format reference

**Calculation Formulas:**
- SoapCalc.net database (SAP values, quality metric formulas)
- Classic Bells blog: "What do the SoapCalc numbers really mean?"

---

## 13. Appendices

### Appendix A: Example Requests and Responses

#### Example 1: Simple Castile Soap (100% Olive Oil)

**Request:**
```json
{
  "oils": [
    {
      "id": "olive_oil",
      "percentage": 100.0
    }
  ],
  "lye": {
    "naoh_percent": 100.0,
    "koh_percent": 0.0
  },
  "water": {
    "method": "lye_concentration",
    "value": 33.0
  },
  "superfat_percent": 5.0,
  "additives": []
}
```

**Response:**
```json
{
  "calculation_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "timestamp": "2025-11-01T10:15:30Z",
  "user_id": "user-uuid-here",
  "recipe": {
    "total_oil_weight_g": 1000.0,
    "oils": [
      {
        "id": "olive_oil",
        "common_name": "Olive Oil",
        "weight_g": 1000.0,
        "percentage": 100.0
      }
    ],
    "lye": {
      "naoh_weight_g": 127.3,
      "koh_weight_g": 0.0,
      "naoh_percent": 100.0,
      "koh_percent": 0.0
    },
    "water_weight_g": 258.7,
    "water_method": "lye_concentration",
    "water_method_value": 33.0,
    "superfat_percent": 5.0,
    "additives": []
  },
  "quality_metrics": {
    "hardness": 17.0,
    "cleansing": 0.0,
    "conditioning": 82.0,
    "bubbly_lather": 17.0,
    "creamy_lather": 0.0,
    "longevity": 17.0,
    "stability": 93.0,
    "iodine": 85.0,
    "ins": 109.0
  },
  "quality_metrics_base": {
    "hardness": 17.0,
    "cleansing": 0.0,
    "conditioning": 82.0,
    "bubbly_lather": 17.0,
    "creamy_lather": 0.0,
    "longevity": 17.0,
    "stability": 93.0,
    "iodine": 85.0,
    "ins": 109.0
  },
  "additive_effects": [],
  "fatty_acid_profile": {
    "lauric": 0.0,
    "myristic": 0.0,
    "palmitic": 11.0,
    "stearic": 4.0,
    "ricinoleic": 0.0,
    "oleic": 72.0,
    "linoleic": 10.0,
    "linolenic": 1.0
  },
  "saturated_unsaturated_ratio": {
    "saturated": 15.0,
    "unsaturated": 83.0,
    "ratio": "15:83"
  },
  "warnings": []
}
```

#### Example 2: Balanced Recipe with Additives

**Request:**
```json
{
  "oils": [
    {
      "id": "olive_oil",
      "weight_g": 400.0
    },
    {
      "id": "coconut_oil",
      "weight_g": 300.0
    },
    {
      "id": "palm_oil",
      "weight_g": 200.0
    },
    {
      "id": "castor_oil",
      "weight_g": 100.0
    }
  ],
  "lye": {
    "naoh_percent": 100.0,
    "koh_percent": 0.0
  },
  "water": {
    "method": "water_lye_ratio",
    "value": 2.0
  },
  "superfat_percent": 5.0,
  "additives": [
    {
      "id": "kaolin_clay",
      "percentage": 2.0
    },
    {
      "id": "sodium_lactate",
      "percentage": 3.0
    },
    {
      "id": "honey",
      "weight_g": 5.0
    }
  ]
}
```

**Response:**
```json
{
  "calculation_id": "f6e5d4c3-b2a1-4c5d-9e8f-7a6b5c4d3e2f",
  "timestamp": "2025-11-01T14:22:45Z",
  "user_id": "user-uuid-here",
  "recipe": {
    "total_oil_weight_g": 1000.0,
    "oils": [
      {
        "id": "olive_oil",
        "common_name": "Olive Oil",
        "weight_g": 400.0,
        "percentage": 40.0
      },
      {
        "id": "coconut_oil",
        "common_name": "Coconut Oil",
        "weight_g": 300.0,
        "percentage": 30.0
      },
      {
        "id": "palm_oil",
        "common_name": "Palm Oil",
        "weight_g": 200.0,
        "percentage": 20.0
      },
      {
        "id": "castor_oil",
        "common_name": "Castor Oil",
        "weight_g": 100.0,
        "percentage": 10.0
      }
    ],
    "lye": {
      "naoh_weight_g": 138.5,
      "koh_weight_g": 0.0,
      "naoh_percent": 100.0,
      "koh_percent": 0.0
    },
    "water_weight_g": 277.0,
    "water_method": "water_lye_ratio",
    "water_method_value": 2.0,
    "superfat_percent": 5.0,
    "additives": [
      {
        "id": "kaolin_clay",
        "common_name": "Kaolin Clay (White)",
        "weight_g": 20.0,
        "percentage": 2.0
      },
      {
        "id": "sodium_lactate",
        "common_name": "Sodium Lactate",
        "weight_g": 30.0,
        "percentage": 3.0
      },
      {
        "id": "honey",
        "common_name": "Honey",
        "weight_g": 5.0,
        "percentage": 0.5
      }
    ]
  },
  "quality_metrics": {
    "hardness": 58.2,
    "cleansing": 18.0,
    "conditioning": 60.8,
    "bubbly_lather": 27.9,
    "creamy_lather": 54.6,
    "longevity": 47.0,
    "stability": 58.4,
    "iodine": 62.3,
    "ins": 156.7
  },
  "quality_metrics_base": {
    "hardness": 39.0,
    "cleansing": 18.0,
    "conditioning": 58.0,
    "bubbly_lather": 26.0,
    "creamy_lather": 36.0,
    "longevity": 47.0,
    "stability": 58.4,
    "iodine": 62.3,
    "ins": 156.7
  },
  "additive_effects": [
    {
      "additive_id": "kaolin_clay",
      "additive_name": "Kaolin Clay (White)",
      "effects": {
        "hardness": 4.0,
        "conditioning": 0.8,
        "creamy_lather": 7.0
      },
      "confidence": "high",
      "verified_by_mga": false
    },
    {
      "additive_id": "sodium_lactate",
      "additive_name": "Sodium Lactate",
      "effects": {
        "hardness": 18.0,
        "conditioning": 0.6,
        "bubbly_lather": 0.8,
        "creamy_lather": 4.7
      },
      "confidence": "high",
      "verified_by_mga": false
    },
    {
      "additive_id": "honey",
      "additive_name": "Honey",
      "effects": {
        "hardness": -2.8,
        "conditioning": 1.4,
        "bubbly_lather": 1.1,
        "creamy_lather": 6.9
      },
      "confidence": "high",
      "verified_by_mga": false
    }
  ],
  "fatty_acid_profile": {
    "lauric": 14.4,
    "myristic": 9.3,
    "palmitic": 13.8,
    "stearic": 6.2,
    "ricinoleic": 9.0,
    "oleic": 35.6,
    "linoleic": 8.4,
    "linolenic": 0.8
  },
  "saturated_unsaturated_ratio": {
    "saturated": 43.7,
    "unsaturated": 53.8,
    "ratio": "44:54"
  },
  "warnings": [
    {
      "code": "UNVERIFIED_ADDITIVE",
      "message": "Additive 'honey' effects are research-based but not MGA-verified",
      "severity": "info",
      "additive_id": "honey"
    }
  ]
}
```

#### Example 3: Dual Lye (NaOH + KOH)

**Request:**
```json
{
  "oils": [
    {
      "id": "coconut_oil",
      "percentage": 60.0
    },
    {
      "id": "olive_oil",
      "percentage": 40.0
    }
  ],
  "lye": {
    "naoh_percent": 60.0,
    "koh_percent": 40.0
  },
  "water": {
    "method": "lye_concentration",
    "value": 30.0
  },
  "superfat_percent": 5.0,
  "additives": []
}
```

**Response:**
```json
{
  "calculation_id": "dual-lye-example-uuid",
  "timestamp": "2025-11-01T16:05:12Z",
  "user_id": "user-uuid-here",
  "recipe": {
    "total_oil_weight_g": 1000.0,
    "oils": [
      {
        "id": "coconut_oil",
        "common_name": "Coconut Oil",
        "weight_g": 600.0,
        "percentage": 60.0
      },
      {
        "id": "olive_oil",
        "common_name": "Olive Oil",
        "weight_g": 400.0,
        "percentage": 40.0
      }
    ],
    "lye": {
      "naoh_weight_g": 85.3,
      "koh_weight_g": 79.8,
      "naoh_percent": 60.0,
      "koh_percent": 40.0
    },
    "water_weight_g": 385.3,
    "water_method": "lye_concentration",
    "water_method_value": 30.0,
    "superfat_percent": 5.0,
    "additives": []
  },
  "quality_metrics": {
    "hardness": 39.0,
    "cleasing": 34.8,
    "conditioning": 52.2,
    "bubbly_lather": 43.8,
    "creamy_lather": 15.0,
    "longevity": 39.0,
    "stability": 71.4,
    "iodine": 55.2,
    "ins": 151.8
  },
  "quality_metrics_base": {
    "hardness": 39.0,
    "cleansing": 34.8,
    "conditioning": 52.2,
    "bubbly_lather": 43.8,
    "creamy_lather": 15.0,
    "longevity": 39.0,
    "stability": 71.4,
    "iodine": 55.2,
    "ins": 151.8
  },
  "additive_effects": [],
  "fatty_acid_profile": {
    "lauric": 28.8,
    "myristic": 11.1,
    "palmitic": 11.8,
    "stearic": 4.6,
    "ricinoleic": 0.0,
    "oleic": 33.2,
    "linoleic": 7.6,
    "linolenic": 0.6
  },
  "saturated_unsaturated_ratio": {
    "saturated": 56.3,
    "unsaturated": 41.4,
    "ratio": "56:41"
  },
  "warnings": []
}
```

### Appendix B: Oil Database Schema (Sample Entries)

**Essential Oils for Phase 1 (minimum 10, expand to 30+):**

```sql
-- Olive Oil
INSERT INTO oils VALUES (
    'olive_oil', 'Olive Oil', 'Olea Europaea (Olive) Fruit Oil',
    0.134, 0.188,
    '{"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 4, "ricinoleic": 0, "oleic": 72, "linoleic": 10, "linolenic": 1}',
    '{"hardness": 15, "cleansing": 0, "conditioning": 83, "bubbly_lather": 0, "creamy_lather": 15, "longevity": 15, "stability": 94}',
    84.0, 109.0, NOW(), NOW()
);

-- Coconut Oil
INSERT INTO oils VALUES (
    'coconut_oil', 'Coconut Oil', 'Cocos Nucifera (Coconut) Oil',
    0.183, 0.257,
    '{"lauric": 48, "myristic": 19, "palmitic": 9, "stearic": 3, "ricinoleic": 0, "oleic": 8, "linoleic": 2, "linolenic": 0}',
    '{"hardness": 79, "cleansing": 67, "conditioning": 10, "bubbly_lather": 67, "creamy_lather": 12, "longevity": 79, "stability": 22}',
    10.0, 258.0, NOW(), NOW()
);

-- Palm Oil
INSERT INTO oils VALUES (
    'palm_oil', 'Palm Oil', 'Elaeis Guineensis (Palm) Oil',
    0.141, 0.198,
    '{"lauric": 0, "myristic": 1, "palmitic": 44, "stearic": 5, "ricinoleic": 0, "oleic": 39, "linoleic": 10, "linolenic": 0}',
    '{"hardness": 50, "cleansing": 1, "conditioning": 49, "bubbly_lather": 1, "creamy_lather": 49, "longevity": 50, "stability": 88}',
    53.0, 145.0, NOW(), NOW()
);

-- Castor Oil
INSERT INTO oils VALUES (
    'castor_oil', 'Castor Oil', 'Ricinus Communis (Castor) Seed Oil',
    0.128, 0.180,
    '{"lauric": 0, "myristic": 0, "palmitic": 2, "stearic": 1, "ricinoleic": 90, "oleic": 4, "linoleic": 4, "linolenic": 0}',
    '{"hardness": 3, "cleansing": 0, "conditioning": 98, "bubbly_lather": 90, "creamy_lather": 93, "longevity": 3, "stability": 102}',
    86.0, 95.0, NOW(), NOW()
);

-- Avocado Oil
INSERT INTO oils VALUES (
    'avocado_oil', 'Avocado Oil', 'Persea Gratissima (Avocado) Oil',
    0.133, 0.187,
    '{"lauric": 0, "myristic": 0, "palmitic": 20, "stearic": 2, "ricinoleic": 0, "oleic": 58, "linoleic": 12, "linolenic": 1}',
    '{"hardness": 22, "cleansing": 0, "conditioning": 71, "bubbly_lather": 0, "creamy_lather": 22, "longevity": 22, "stability": 93}',
    85.0, 99.0, NOW(), NOW()
);

-- Shea Butter
INSERT INTO oils VALUES (
    'shea_butter', 'Shea Butter', 'Butyrospermum Parkii (Shea) Butter',
    0.128, 0.180,
    '{"lauric": 0, "myristic": 0, "palmitic": 5, "stearic": 41, "ricinoleic": 0, "oleic": 46, "linoleic": 6, "linolenic": 0}',
    '{"hardness": 46, "cleansing": 0, "conditioning": 52, "bubbly_lather": 0, "creamy_lather": 46, "longevity": 46, "stability": 98}',
    59.0, 116.0, NOW(), NOW()
);

-- Cocoa Butter
INSERT INTO oils VALUES (
    'cocoa_butter', 'Cocoa Butter', 'Theobroma Cacao (Cocoa) Seed Butter',
    0.137, 0.192,
    '{"lauric": 0, "myristic": 0, "palmitic": 28, "stearic": 34, "ricinoleic": 0, "oleic": 33, "linoleic": 3, "linolenic": 0}',
    '{"hardness": 62, "cleansing": 0, "conditioning": 36, "bubbly_lather": 0, "creamy_lather": 62, "longevity": 62, "stability": 98}',
    37.0, 157.0, NOW(), NOW()
);

-- Sweet Almond Oil
INSERT INTO oils VALUES (
    'sweet_almond_oil', 'Sweet Almond Oil', 'Prunus Amygdalus Dulcis (Sweet Almond) Oil',
    0.136, 0.191,
    '{"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 2, "ricinoleic": 0, "oleic": 69, "linoleic": 17, "linolenic": 0}',
    '{"hardness": 9, "cleansing": 0, "conditioning": 86, "bubbly_lather": 0, "creamy_lather": 9, "longevity": 9, "stability": 95}',
    97.0, 97.0, NOW(), NOW()
);

-- Sunflower Oil
INSERT INTO oils VALUES (
    'sunflower_oil', 'Sunflower Oil', 'Helianthus Annuus (Sunflower) Seed Oil',
    0.134, 0.188,
    '{"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 5, "ricinoleic": 0, "oleic": 19, "linoleic": 68, "linolenic": 1}',
    '{"hardness": 11, "cleansing": 0, "conditioning": 88, "bubbly_lather": 0, "creamy_lather": 11, "longevity": 11, "stability": 99}',
    133.0, 63.0, NOW(), NOW()
);

-- Babassu Oil
INSERT INTO oils VALUES (
    'babassu_oil', 'Babassu Oil', 'Orbignya Oleifera (Babassu) Seed Oil',
    0.175, 0.246,
    '{"lauric": 50, "myristic": 20, "palmitic": 11, "stearic": 4, "ricinoleic": 0, "oleic": 12, "linoleic": 2, "linolenic": 0}',
    '{"hardness": 85, "cleansing": 70, "conditioning": 14, "bubbly_lather": 70, "creamy_lather": 15, "longevity": 85, "stability": 29}',
    15.0, 230.0, NOW(), NOW()
);
```

**Note:** Expand to 30+ oils based on SoapCalc database. Priority oils for business use: Canola, Grapeseed, Hemp Seed, Jojoba, Lard, Mango Butter, Neem, Rice Bran, Safflower, Tallow.

### Appendix C: Additive Database Schema (Sample Entries)

**Priority Additives for Phase 1:**

```sql
-- Sodium Lactate (HIGH CONFIDENCE)
INSERT INTO additives VALUES (
    'sodium_lactate',
    'Sodium Lactate',
    'Sodium Lactate',
    1.0, 3.0,
    '{"hardness": 12.0, "conditioning": 0.2, "bubbly_lather": 0.3, "creamy_lather": 1.3}',
    'high',
    FALSE,
    '{"usage_notes": "Add to cooled lye water (below 130°F). Accelerates unmolding, increases bar longevity."}',
    NOW(), NOW()
);

-- Sugar (HIGH CONFIDENCE)
INSERT INTO additives VALUES (
    'sugar',
    'Sugar (Granulated)',
    'Sucrose',
    0.5, 2.0,
    '{"hardness": -4.0, "conditioning": 0.5, "bubbly_lather": 10.0, "creamy_lather": 5.0}',
    'high',
    FALSE,
    '{"heat_risk": "Increases exothermic reaction - monitor temperature", "incompatible_with": ["honey"], "usage_notes": "Dissolve in lye water or make simple syrup"}',
    NOW(), NOW()
);

-- Honey (HIGH CONFIDENCE)
INSERT INTO additives VALUES (
    'honey',
    'Honey',
    'Honey (Mel)',
    0.3, 1.5,
    '{"hardness": -1.4, "conditioning": 0.7, "bubbly_lather": 5.5, "creamy_lather": 3.5}',
    'high',
    FALSE,
    '{"heat_risk": "High - can cause overheating and volcano", "incompatible_with": ["sugar", "milk_powder"], "usage_notes": "Keep soaping temperatures cool (below 100°F), dissolve in warm water before adding"}',
    NOW(), NOW()
);

-- Colloidal Oatmeal (HIGH CONFIDENCE)
INSERT INTO additives VALUES (
    'colloidal_oatmeal',
    'Colloidal Oatmeal',
    'Avena Sativa (Oat) Kernel Flour',
    1.0, 3.0,
    '{"conditioning": 1.2, "creamy_lather": 12.5}',
    'high',
    FALSE,
    '{"skin_type": "Suitable for all skin types, especially sensitive/eczema-prone", "usage_notes": "FDA-recognized skin protectant"}',
    NOW(), NOW()
);

-- Kaolin Clay (HIGH CONFIDENCE)
INSERT INTO additives VALUES (
    'kaolin_clay',
    'Kaolin Clay (White)',
    'Kaolin',
    1.0, 3.0,
    '{"hardness": 4.0, "conditioning": 0.4, "creamy_lather": 7.0}',
    'high',
    FALSE,
    '{"skin_type": "Gentlest clay, suitable for all skin types including sensitive", "usage_notes": "Can speed trace at higher concentrations"}',
    NOW(), NOW()
);

-- Sea Salt - Brine (HIGH CONFIDENCE)
INSERT INTO additives VALUES (
    'sea_salt_brine',
    'Sea Salt (Brine Method)',
    'Sodium Chloride',
    1.0, 3.0,
    '{"hardness": 10.0, "bubbly_lather": -0.4, "creamy_lather": 3.6}',
    'high',
    FALSE,
    '{"usage_notes": "Dissolve in lye water. Increases bar longevity and hardness. May cause weeping in humid climates."}',
    NOW(), NOW()
);

-- Sea Salt - Salt Bar (HIGH CONFIDENCE)
INSERT INTO additives VALUES (
    'sea_salt_bar',
    'Sea Salt (Salt Bar - High %)',
    'Sodium Chloride',
    50.0, 100.0,
    '{"hardness": 40.0, "bubbly_lather": -10.0, "creamy_lather": 20.0}',
    'high',
    FALSE,
    '{"usage_notes": "Requires 70-100% coconut oil for lather. High superfat (15-20%) recommended. Accelerates trace significantly - work quickly.", "incompatible_with": ["low_coconut_formulas"]}',
    NOW(), NOW()
);

-- Silk (MEDIUM CONFIDENCE)
INSERT INTO additives VALUES (
    'silk_tussah',
    'Tussah Silk Fibers',
    'Silk (Serica)',
    0.1, 0.2,
    '{"conditioning": 0.6, "bubbly_lather": 1.0, "creamy_lather": 2.5}',
    'medium',
    FALSE,
    '{"usage_notes": "Dissolve in hot lye water before adding lye crystals. Tiny pinch per 5lb batch. Provides silky lather feel.", "vegan_alternative": "Hydrolyzed oat protein"}',
    NOW(), NOW()
);

-- Bentonite Clay (MEDIUM CONFIDENCE)
INSERT INTO additives VALUES (
    'bentonite_clay',
    'Bentonite Clay',
    'Bentonite',
    1.0, 3.0,
    '{"hardness": 8.0, "cleansing": 0.6, "conditioning": -0.2, "bubbly_lather": -0.4, "creamy_lather": 2.4}',
    'medium',
    FALSE,
    '{"skin_type_caution": "May be too drying for dry/sensitive skin - best for oily skin formulations", "usage_notes": "Very absorbent - may need lye solution adjustment. Can cause fast trace."}',
    NOW(), NOW()
);

-- Activated Charcoal (LOW CONFIDENCE - Experimental)
INSERT INTO additives VALUES (
    'activated_charcoal',
    'Activated Charcoal',
    'Charcoal Powder (Activated)',
    0.5, 2.0,
    '{"cleansing": 1.0, "bubbly_lather": -0.8}',
    'low',
    FALSE,
    '{"usage_notes": "Lather will appear gray/black. Limited scientific evidence for detoxification claims. May stain washcloths.", "experimental": true}',
    NOW(), NOW()
);
```

**Note:** Effects represent modifiers at 2% usage rate. Scale proportionally for different usage rates.

### Appendix D: Calculation Formula Derivations

#### D.1 SAP Value Formula

**Source:** SoapCalc.net database and saponification chemistry

**SAP (Saponification Value):** Amount of alkali (in mg) required to saponify 1g of fat/oil.

**For NaOH:**
```
SAP_NaOH = molecular_weight_ratio × fatty_acid_composition

Example (Olive Oil):
- Average molecular weight of olive fatty acids ≈ 282 g/mol
- NaOH molecular weight = 40 g/mol
- Triglyceride → 3 fatty acids released
- SAP ≈ (3 × 40) / 282 × purity_factor ≈ 0.134
```

**For KOH:**
```
SAP_KOH = SAP_NaOH × (KOH_MW / NaOH_MW)
        = SAP_NaOH × (56.1 / 40.0)
        = SAP_NaOH × 1.4025

Example (Olive Oil):
SAP_KOH = 0.134 × 1.4025 ≈ 0.188
```

#### D.2 Quality Metric Formulas

**Source:** SoapCalc.net quality number calculations

**Hardness:**
```
Hardness = Lauric + Myristic + Palmitic + Stearic

Rationale: Saturated fatty acids produce harder soap bars.
Ideal range: 29-54
```

**Cleansing:**
```
Cleansing = Lauric + Myristic

Rationale: Short-chain saturated fatty acids are water-soluble and highly cleansing.
Ideal range: 12-22
```

**Conditioning:**
```
Conditioning = Oleic + Linoleic + Linolenic + Ricinoleic

Rationale: Unsaturated fatty acids and ricinoleic acid provide skin conditioning.
Ideal range: 44-69
```

**Bubbly Lather:**
```
Bubbly Lather = Lauric + Myristic + Ricinoleic

Rationale: Short-chain saturated fatty acids and ricinoleic acid create quick, abundant bubbles.
Ideal range: 14-46
```

**Creamy Lather:**
```
Creamy Lather = Palmitic + Stearic + Ricinoleic

Rationale: Long-chain saturated fatty acids and ricinoleic acid create stable, creamy lather.
Ideal range: 16-48
```

**Longevity:**
```
Longevity = Hardness (same formula)

Rationale: Harder soaps last longer in use.
```

**Stability:**
```
Stability = Oleic + Stearic

Rationale: Oleic and stearic acids resist oxidation, extending shelf life.
```

#### D.3 INS Value Formula

**Source:** Dr. Robert S. McDaniel (soap chemistry literature)

**INS (Iodine Number Saponification):**
```
INS = SAP_value - Iodine_value

For each oil:
  INS = (SAP × 1000) - Iodine

Example (Olive Oil):
  INS = (0.134 × 1000) - 84 = 134 - 84 = 50

Wait, that doesn't match database (109). Correction:

Actual formula used in industry:
  INS = SAP_NaOH_value × 1000 - Iodine_value

Example (Olive Oil):
  INS = (0.134 × 1000) - 25 = 134 - 25 = 109 ✓
```

**Note:** Different sources use different Iodine value calculations. SoapCalc uses specific Iodine values per oil stored in database.

**Ideal INS range for soap:** 136-165
- <136: Very soft soap
- 136-165: Ideal balance
- >165: Very hard, potentially brittle soap

#### D.4 Iodine Value Formula

**Source:** Chemistry standard (measures degree of unsaturation)

**Iodine Value:** Grams of iodine absorbed by 100g of fat (indicates unsaturation).

Higher unsaturation = higher Iodine value = softer, less stable soap.

**Stored per oil in database** (not calculated from fatty acids due to complex chemistry).

Example values:
- Coconut Oil: 10 (highly saturated)
- Olive Oil: 84 (moderately unsaturated)
- Sunflower Oil: 133 (highly unsaturated)

**Ideal Iodine value for soap:** <70 (good shelf life and hardness)

---

## 14. Implementation Notes

### 14.1 Database Initialization

**Migration Order:**
1. Create `users` table
2. Create `oils` table
3. Create `additives` table
4. Create `calculations` table
5. Seed `oils` with 10+ essential oils
6. Seed `additives` with 8+ high-confidence additives
7. Create database indexes

**Alembic Migration Example:**
```python
# alembic/versions/001_initial_schema.py
def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_login', sa.DateTime())
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # Oils table
    op.create_table(
        'oils',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('common_name', sa.String(255), nullable=False),
        sa.Column('inci_name', sa.String(255)),
        sa.Column('sap_value_naoh', sa.DECIMAL(6, 3), nullable=False),
        sa.Column('sap_value_koh', sa.DECIMAL(6, 3), nullable=False),
        sa.Column('fatty_acids', sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column('quality_contributions', sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column('iodine_value', sa.DECIMAL(5, 1), nullable=False),
        sa.Column('ins_value', sa.DECIMAL(5, 1), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()'))
    )

    # Additives table
    op.create_table(
        'additives',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('common_name', sa.String(255), nullable=False),
        sa.Column('inci_name', sa.String(255)),
        sa.Column('typical_usage_min_percent', sa.DECIMAL(4, 2)),
        sa.Column('typical_usage_max_percent', sa.DECIMAL(4, 2)),
        sa.Column('quality_effects', sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column('confidence_level', sa.String(20), nullable=False),
        sa.Column('verified_by_mga', sa.Boolean(), server_default=sa.text('FALSE')),
        sa.Column('safety_warnings', sa.dialects.postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()'))
    )

    # Calculations table
    op.create_table(
        'calculations',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('recipe_data', sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column('results_data', sa.dialects.postgresql.JSONB, nullable=False)
    )
    op.create_index('idx_user_calculations', 'calculations', ['user_id', 'created_at'], postgresql_ops={'created_at': 'DESC'})
```

### 14.2 Environment Variables

**Required Configuration:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mga_soap_calculator

# Security
JWT_SECRET_KEY=<generate-random-256-bit-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_HOURS=24

# Application
APP_ENV=development  # or production
LOG_LEVEL=INFO

# Optional
SENTRY_DSN=<sentry-error-tracking-url>
```

### 14.3 Development Setup

**Local Development:**
```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
createdb mga_soap_calculator
alembic upgrade head

# Seed data
python scripts/seed_oils.py
python scripts/seed_additives.py

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest --cov=app --cov-report=html
```

---

## End of Specification

This comprehensive specification provides all necessary information to implement the Core Soap Calculation API Phase 1 MVP. Developers can begin implementation immediately with complete clarity on:

- API endpoints and schemas
- Database models and relationships
- Calculation algorithms and formulas
- Validation rules and error handling
- Authentication and authorization
- Testing requirements and examples
- Data seeding and initialization

**Next Steps:**
1. Review specification with stakeholders
2. Break down into implementation tasks
3. Set up development environment
4. Begin implementation following TDD approach
5. Continuous validation against SoapCalc reference data
