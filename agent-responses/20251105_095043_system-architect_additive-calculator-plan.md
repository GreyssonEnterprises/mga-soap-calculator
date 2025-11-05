# System Architect - Smart Additive Calculator Implementation Plan

**Timestamp:** 2025-11-05 09:50:43
**Task:** Generate implementation plan for Feature 004 (Smart Additive Calculator)
**Requestor:** Bob

## Executive Summary

Comprehensive implementation plan for automatic additive amount calculations with intelligent usage recommendations. Database extension accommodates 122 ingredients (19 additives + 24 essential oils + 79 colorants) with safety warnings, preparation instructions, and category-based organization.

**Technical Approach:**
- Extend existing Additive model with calculator-specific fields
- Create two new models: EssentialOil and Colorant (parallel structure)
- New recommendation endpoints returning light/standard/heavy calculations
- Enhanced recipe calculation accepting additive selections with auto-calculation
- Import scripts for 122 ingredients from validated JSON sources

**Complexity:** MEDIUM
**Risk:** LOW (extends existing patterns, no architectural changes)
**Timeline:** ~5 days implementation + 2 days testing

---

## Phase 0: Technical Context & Research

### Technical Stack Context

**Language/Version:** Python 3.11+
**Primary Dependencies:** FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL 15+
**Storage:** PostgreSQL with JSONB for flexible metadata
**Testing:** pytest, pytest-cov, httpx (API integration tests)
**Target Platform:** Linux server (Fedora 42 with Podman/Quadlet deployment)
**Project Type:** Single backend API (Phase 1 scope - no frontend)

### Performance Goals

**API Response Time:** <50ms for recommendation calculations (spec requirement)
**Database Queries:** <50ms for ingredient lookups (indexed by id and common_name)
**Calculation Throughput:** Support 100+ concurrent requests
**Formula Complexity:** Simple percentage calculation `(batch_size_g × usage_pct) / 100`

### Constraints

**Data Integrity:** 122 ingredients pre-populated from validated JSON sources
**Research Backing:** Usage rates sourced from supplier guidelines and CPSR data
**Safety Critical:** Warning system must flag all problematic ingredient behaviors
**Backward Compatibility:** Extends existing Additive model without breaking changes

### Scale/Scope

**Ingredients:** 122 total (19 additives + 24 essential oils + 79 colorants)
**API Endpoints:** 8 new endpoints (3 recommendation, 3 listing, 2 enhanced calculate)
**Database Tables:** Extend 1 existing (additives), create 2 new (essential_oils, colorants)
**Test Coverage:** 90%+ coverage requirement (constitution compliance)

---

## Constitution Check

### ✅ I. API-First Architecture
**Status:** COMPLIANT
**Evidence:** All features expose REST API endpoints before UI implementation.

- Recommendation endpoints: `GET /api/v1/additives/{id}/recommend`
- Essential oil endpoints: `GET /api/v1/essential-oils/{id}/recommend`
- Colorant listing: `GET /api/v1/colorants?category={color}`
- Enhanced calculate: `POST /api/v1/calculate` (accepts additive selections)
- FastAPI automatic OpenAPI documentation generated
- All endpoints testable via httpx integration tests
- No frontend implementation in Phase 1

**Action:** No violations. Feature is API-only per Phase 1 scope.

---

### ✅ II. Research-Backed Calculations
**Status:** COMPLIANT
**Evidence:** All usage rates sourced from documented references.

**Data Sources:**
- `additives-usage-reference.json`: 19 ingredients with supplier-validated usage rates
- `essential-oils-usage-reference.json`: 24 EOs with CPSR-validated max rates (0.025%-3%)
- `natural-colorants-reference.json`: 79 colorants with method-specific application rates

**Validation Strategy:**
- Source tracking: `confidence_level` field (high/medium/low) per ingredient
- Research citations: Store botanical names, method references in database
- MGA verification: `verified_by_mga` boolean for empirically tested ingredients
- Warning system: Document problematic behaviors (accelerates_trace, causes_overheating)

**Calculation Formula:**
```python
amount_g = (batch_size_g × usage_percent) / 100
```

**Property-Based Tests:**
- Test usage rate boundaries (min/max validation)
- Test warning thresholds (over-usage detection)
- Test calculation edge cases (zero batch, extreme percentages)

**Action:** Document source references in database metadata. Add inline citations to calculation logic.

---

### ✅ III. Test-First Development
**Status:** COMPLIANT
**Enforcement:** TDD cycle mandatory per constitution.

**Test Strategy:**
1. **Model Tests** (unit): Entity validation, field constraints, JSONB structure
2. **Import Script Tests** (unit): JSON parsing, data transformation, database insertion
3. **API Endpoint Tests** (integration): Request/response validation, pagination, filtering
4. **Calculation Tests** (property-based): Edge cases, warning triggers, percentage boundaries
5. **Contract Tests** (integration): Enhanced calculate endpoint with additive selections

**Coverage Target:** >90% (pytest-cov enforcement)

**Test Order (TDD Cycle):**
```
1. Write model tests → Implement models
2. Write import tests → Implement import scripts
3. Write API tests → Implement endpoints
4. Write calculation tests → Implement recommendation logic
5. Run full suite → Refactor → Verify coverage
```

**Action:** All test files must exist BEFORE implementation code. Red-Green-Refactor cycle strictly enforced.

---

### ✅ IV. Data Integrity & ACID Compliance
**Status:** COMPLIANT
**Evidence:** PostgreSQL transactions, foreign keys, Alembic migrations.

**Migration Strategy:**
- **Migration 1:** Extend `additives` table with new fields (ALTER TABLE)
  - Add: `usage_rate_standard_percent`, `when_to_add`, `preparation_instructions`
  - Add: `mixing_tips`, `category`, boolean flags for warnings
  - Preserve existing data (backward compatible)

- **Migration 2:** Create `essential_oils` table
  - Fields: `id`, `common_name`, `botanical_name`, `max_usage_rate_pct`
  - Additional: `scent_profile`, `blends_with`, `note`, `category`, `warnings`
  - Foreign key: None (standalone reference table)

- **Migration 3:** Create `colorants` table
  - Fields: `id`, `common_name`, `botanical_name`, `category` (color family)
  - Additional: `usage`, `method`, `color_range`, `warnings`
  - Foreign key: None (standalone reference table)

**ACID Guarantees:**
- Import scripts use database transactions (rollback on failure)
- No eventual consistency - immediate read-after-write
- Foreign key constraints enforced at database level
- Alembic migration versioning (immutable, sequential)

**Action:** Three separate migrations (one per table change). Test rollback procedures.

---

### ✅ V. Performance Budgets
**Status:** COMPLIANT
**Evidence:** Calculation endpoint <50ms per spec requirement.

**Performance Targets:**
- **Calculation Response:** <50ms (spec requirement)
- **Database Queries:** <50ms (indexed lookups by id, common_name)
- **List Endpoints:** <200ms (pagination pattern from existing resources.py)
- **Concurrent Load:** Support 100+ requests (async SQLAlchemy)

**Optimization Strategy:**
- Database indexes: PRIMARY KEY (id), INDEX (common_name), INDEX (category)
- Query optimization: Use existing pagination pattern from `list_oils()`
- Calculation caching: None required (formula is trivial)
- Connection pooling: Async SQLAlchemy connection pool

**Load Testing Plan:**
- Locust or Apache Bench for concurrent request testing
- Target: 100 concurrent requests, <50ms p95 latency
- Validate before merging to main

**Action:** Add database indexes. Verify with EXPLAIN ANALYZE. Load test before merge.

---

### ✅ VI. Security & Authentication
**Status:** COMPLIANT (with note)
**Evidence:** Public reference endpoints require no authentication per existing pattern.

**Authentication Status:**
- Resource discovery endpoints: **No authentication** (public reference data)
  - `/api/v1/oils` - public
  - `/api/v1/additives` - public (existing)
  - `/api/v1/essential-oils` - public (new)
  - `/api/v1/colorants` - public (new)
  - `/api/v1/additives/{id}/recommend` - public (new)

- Recipe calculation: **JWT required** (per existing `/api/v1/calculate`)
  - Enhanced endpoint maintains existing auth

**Rationale:** Usage rate reference data is public knowledge (supplier catalogs, CPSR data). Recipe formulations are proprietary (require auth).

**Input Validation:**
- Pydantic models for all request bodies
- Query parameter validation (limit, offset, search)
- Usage percentage bounds (0.0 - 100.0)
- Batch size validation (positive float)

**Action:** Maintain existing auth pattern. Pydantic validation for all inputs.

---

### ✅ VII. Deployment Platform Standards
**Status:** COMPLIANT
**Evidence:** Fedora + Podman + Quadlet deployment per constitution.

**Container Updates:**
- Base image: Fedora or UBI (matches existing Dockerfile)
- No new containers required (extends existing FastAPI service)
- Quadlet configuration: No changes (API endpoints added to existing service)
- Ansible playbook: Add database migration step for new tables

**Deployment Steps:**
1. Run Alembic migrations: `alembic upgrade head`
2. Run import scripts: `python scripts/import_additives_extended.py`
3. Restart FastAPI service: `systemctl --user restart soap-calculator`
4. Verify endpoints: `curl localhost:8000/api/v1/essential-oils`

**Action:** Update Ansible playbook with migration and import steps. Test on staging first.

---

### ✅ VIII. Observability & Monitoring
**Status:** COMPLIANT
**Evidence:** Structured logging and error tracking.

**Logging Strategy:**
- Structured JSON logs with request IDs (existing pattern)
- Log levels: INFO (successful calculations), WARNING (usage over max), ERROR (validation failures)
- Context: Include ingredient ID, batch size, calculated amounts in logs

**Error Tracking:**
- Sentry integration for unhandled exceptions
- Custom exceptions for domain errors (InvalidUsageRate, IngredientNotFound)
- Prometheus metrics: response_time, request_count, error_rate per endpoint

**Monitoring Targets:**
- Response time p95 <50ms (alert if >100ms)
- Error rate <0.1% (alert if >1%)
- Database query time <50ms (alert if >100ms)

**Action:** Add structured logging to new endpoints. Verify Sentry captures new exception types.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-additive-calculator/
├── spec.md              # Feature specification (EXISTS)
├── plan.md              # This implementation plan (WILL CREATE)
├── research.md          # Phase 0 research (SKIP - data sources validated)
├── data-model.md        # Phase 1 database design (WILL CREATE)
├── quickstart.md        # Phase 1 API usage examples (WILL CREATE)
├── contracts/           # Phase 1 API contracts (WILL CREATE)
│   ├── additives-recommend.md
│   ├── essential-oils-list.md
│   ├── essential-oils-recommend.md
│   ├── colorants-list.md
│   └── calculate-enhanced.md
└── tasks.md             # Phase 2 task breakdown (CREATED BY /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── models/
│   ├── additive.py           # EXTEND (add calculator fields)
│   ├── essential_oil.py      # NEW (EO entity with usage rates)
│   └── colorant.py           # NEW (colorant entity with methods)
│
├── schemas/
│   ├── resource.py           # EXTEND (add EO and Colorant schemas)
│   ├── recommendation.py     # NEW (recommendation response schemas)
│   └── calculate.py          # EXTEND (accept additive selections)
│
├── api/v1/
│   ├── resources.py          # EXTEND (add EO and colorant endpoints)
│   ├── recommendations.py    # NEW (recommendation logic)
│   └── calculate.py          # EXTEND (process additive selections)
│
└── services/
    └── calculator.py         # EXTEND (additive calculation logic)

scripts/
├── import_additives_extended.py   # NEW (import 19 additives with new fields)
├── import_essential_oils.py       # NEW (import 24 EOs)
└── import_colorants.py            # NEW (import 79 colorants)

tests/
├── unit/
│   ├── test_additive_model.py       # EXTEND (new field validation)
│   ├── test_essential_oil_model.py  # NEW (EO model tests)
│   ├── test_colorant_model.py       # NEW (colorant model tests)
│   ├── test_import_additives.py     # NEW (import script tests)
│   ├── test_import_eos.py           # NEW (EO import tests)
│   └── test_import_colorants.py     # NEW (colorant import tests)
│
├── integration/
│   ├── test_resources_api.py        # EXTEND (EO and colorant endpoints)
│   ├── test_recommendations_api.py  # NEW (recommendation endpoint tests)
│   └── test_calculate_enhanced.py   # NEW (enhanced calculate tests)
│
└── contract/
    └── test_recommendation_contracts.py  # NEW (API contract validation)

alembic/versions/
├── YYYYMMDD_HHMM_extend_additives_table.py       # Migration 1
├── YYYYMMDD_HHMM_create_essential_oils_table.py  # Migration 2
└── YYYYMMDD_HHMM_create_colorants_table.py       # Migration 3
```

**Structure Decision:** Single project architecture (existing pattern). Extends current FastAPI backend with new models, endpoints, and services. No new infrastructure required.

---

## Complexity Tracking

**No constitution violations requiring justification.**

All implementation follows existing patterns:
- Model extension pattern (from Oil model)
- Pagination pattern (from `list_oils()` endpoint)
- Calculation logic (simple formula, no complex algorithms)
- Database seeding (from existing `seed_database.py`)

---

## Phase 1: Design Artifacts

### 1.1 Data Model Design (`data-model.md`)

#### Extended Additive Entity

**Purpose:** Add calculator-specific fields to existing Additive model (backward compatible).

**New Fields:**
```python
class Additive(Base):
    # EXISTING FIELDS (preserved)
    id: str
    common_name: str
    inci_name: str
    typical_usage_min_percent: float
    typical_usage_max_percent: float
    quality_effects: dict (JSONB)
    confidence_level: str
    verified_by_mga: bool
    safety_warnings: dict (JSONB)

    # NEW FIELDS (Phase 1)
    usage_rate_standard_percent: float  # Recommended "standard" usage
    when_to_add: str                    # "to oils", "to lye water", "at trace"
    preparation_instructions: str       # "Disperse in water", "Melt first"
    mixing_tips: str                    # Best practices for incorporation
    category: str                       # "exfoliant", "lather_booster", etc.
    accelerates_trace: bool             # Warning flag
    causes_overheating: bool            # Warning flag
    can_be_scratchy: bool               # Warning flag
    turns_brown: bool                   # Warning flag
```

**Data Example** (Honey):
```json
{
  "id": "honey",
  "common_name": "Honey",
  "inci_name": "Mel",
  "typical_usage_min_percent": 1.0,
  "typical_usage_max_percent": 3.0,
  "usage_rate_standard_percent": 2.0,
  "when_to_add": "to warm oils before mixing lye",
  "preparation_instructions": "Warm slightly to ensure liquidity",
  "mixing_tips": "Add to oils, stir well, then add lye solution",
  "category": "lather_booster",
  "accelerates_trace": true,
  "causes_overheating": true,
  "can_be_scratchy": false,
  "turns_brown": false,
  "quality_effects": {
    "hardness": 0, "cleansing": 0, "conditioning": 2,
    "bubbly": 5, "creamy": 3, "moisturizing": 2, "silky": 1
  },
  "confidence_level": "high",
  "verified_by_mga": true
}
```

**Migration Strategy:**
- ALTER TABLE to add new columns (nullable initially)
- Backfill with default values for existing rows
- Run import script to update with proper data
- Set NOT NULL constraints after backfill

---

#### Essential Oil Entity (NEW)

**Purpose:** Store essential oil usage rates with safety limits and blending guidance.

**Schema:**
```python
class EssentialOil(Base):
    __tablename__ = "essential_oils"

    id: str                          # PRIMARY KEY (e.g., "lavender-english")
    common_name: str                 # "Lavender (English)"
    botanical_name: str              # "Lavandula augustifolia"
    max_usage_rate_pct: float        # Max safe rate (0.025% to 3%)
    scent_profile: str               # "Sweet, herbaceous, and floral"
    usage_notes: str                 # Application guidance
    blends_with: list[str] (JSONB)   # ["Bergamot", "Chamomile", ...]
    note: str                        # "Top", "Middle", "Base"
    category: str                    # "floral", "citrus", "herbal", etc.
    warnings: str (nullable)         # "Can fade quickly" or "Accelerates trace"
    color_effect: str (nullable)     # "Slightly yellow" (May Chang)

    created_at: datetime
    updated_at: datetime
```

**Data Example** (Lavender):
```json
{
  "id": "lavender-english",
  "common_name": "Lavender (English)",
  "botanical_name": "Lavandula augustifolia",
  "max_usage_rate_pct": 3.0,
  "scent_profile": "Sweet, herbaceous, and floral",
  "usage_notes": "Long used in perfume industry, blends well with many other EOs",
  "blends_with": ["Bergamot", "Chamomile", "Geranium", "Grapefruit"],
  "note": "Middle",
  "category": "floral",
  "warnings": null,
  "color_effect": null
}
```

**Indexes:**
- PRIMARY KEY: `id`
- INDEX: `common_name` (for search)
- INDEX: `category` (for filtering)

---

#### Colorant Entity (NEW)

**Purpose:** Store natural colorant usage rates with method-specific application guidance.

**Schema:**
```python
class Colorant(Base):
    __tablename__ = "colorants"

    id: str                       # PRIMARY KEY (e.g., "turmeric-yellow")
    common_name: str              # "Turmeric"
    botanical_name: str           # "Curcuma longa"
    category: str                 # Color family: "yellow", "orange", "pink", etc.
    usage: str                    # "1/32 tsp (yellow) to 1 tsp (orange) PPO"
    method: str                   # "Add to lye or at trace, premix in oil"
    color_range: str              # "Pale yellow to burnt orange"
    warnings: str (nullable)      # "Does not disperse in water"
    notes: str (nullable)         # Additional application notes

    created_at: datetime
    updated_at: datetime
```

**Data Example** (Turmeric):
```json
{
  "id": "turmeric-yellow",
  "common_name": "Turmeric",
  "botanical_name": "Curcuma longa",
  "category": "yellow",
  "usage": "1/32 tsp (yellow) to 1 tsp (orange) PPO",
  "method": "Add to lye or at trace, premix in oil",
  "color_range": "Pale yellow to burnt orange",
  "warnings": "Does not disperse in water",
  "notes": null
}
```

**Indexes:**
- PRIMARY KEY: `id`
- INDEX: `category` (for color family filtering)
- INDEX: `common_name` (for search)

---

### 1.2 API Contracts (`contracts/`)

#### Contract 1: Additive Recommendation

**File:** `contracts/additives-recommend.md`

**Endpoint:** `GET /api/v1/additives/{id}/recommend`

**Query Parameters:**
- `batch_size_g` (required): Batch size in grams (positive float)

**Response Schema:**
```json
{
  "additive_id": "honey",
  "common_name": "Honey",
  "batch_size_g": 500.0,
  "recommendations": {
    "light": {
      "usage_percent": 1.0,
      "amount_g": 5.0,
      "amount_oz": 0.18
    },
    "standard": {
      "usage_percent": 2.0,
      "amount_g": 10.0,
      "amount_oz": 0.35
    },
    "heavy": {
      "usage_percent": 3.0,
      "amount_g": 15.0,
      "amount_oz": 0.53
    }
  },
  "usage_guidance": {
    "when_to_add": "to warm oils before mixing lye",
    "preparation_instructions": "Warm slightly to ensure liquidity",
    "mixing_tips": "Add to oils, stir well, then add lye solution"
  },
  "warnings": [
    "Can cause soap to accelerate trace",
    "May cause overheating in large batches"
  ]
}
```

**Calculation Logic:**
```python
def calculate_amount(batch_size_g: float, usage_pct: float) -> dict:
    amount_g = (batch_size_g * usage_pct) / 100
    amount_oz = amount_g / 28.35  # grams to ounces conversion
    return {
        "usage_percent": usage_pct,
        "amount_g": round(amount_g, 1),
        "amount_oz": round(amount_oz, 2)
    }
```

**Warning Logic:**
```python
def build_warnings(additive: Additive) -> list[str]:
    warnings = []
    if additive.accelerates_trace:
        warnings.append("Can cause soap to accelerate trace")
    if additive.causes_overheating:
        warnings.append("May cause overheating in large batches")
    if additive.can_be_scratchy:
        warnings.append("Can be scratchy or exfoliating on skin")
    if additive.turns_brown:
        warnings.append("May turn brown or discolor in soap")
    return warnings
```

**Error Cases:**
- 404: Additive ID not found
- 400: Invalid batch_size_g (non-positive or missing)
- 500: Database connection error

---

#### Contract 2: Essential Oils List

**File:** `contracts/essential-oils-list.md`

**Endpoint:** `GET /api/v1/essential-oils`

**Query Parameters:**
- `limit` (optional): Items per page (1-100, default 50)
- `offset` (optional): Pagination offset (default 0)
- `search` (optional): Search by common name or botanical name
- `category` (optional): Filter by category ("floral", "citrus", "herbal", etc.)
- `note` (optional): Filter by note type ("Top", "Middle", "Base")
- `sort_by` (optional): "common_name", "max_usage_rate_pct" (default: common_name)
- `sort_order` (optional): "asc", "desc" (default: asc)

**Response Schema:**
```json
{
  "essential_oils": [
    {
      "id": "lavender-english",
      "common_name": "Lavender (English)",
      "botanical_name": "Lavandula augustifolia",
      "max_usage_rate_pct": 3.0,
      "scent_profile": "Sweet, herbaceous, and floral",
      "note": "Middle",
      "category": "floral",
      "warnings": null
    }
  ],
  "total_count": 24,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

**Implementation:** Follow existing `list_oils()` pattern from `resources.py`.

---

#### Contract 3: Essential Oil Recommendation

**File:** `contracts/essential-oils-recommend.md`

**Endpoint:** `GET /api/v1/essential-oils/{id}/recommend`

**Query Parameters:**
- `batch_size_g` (required): Batch size in grams

**Response Schema:**
```json
{
  "essential_oil_id": "lavender-english",
  "common_name": "Lavender (English)",
  "batch_size_g": 500.0,
  "max_safe_amount": {
    "usage_percent": 3.0,
    "amount_g": 15.0,
    "amount_oz": 0.53
  },
  "scent_profile": "Sweet, herbaceous, and floral",
  "blending_guidance": {
    "note": "Middle",
    "blends_well_with": ["Bergamot", "Chamomile", "Geranium"]
  },
  "warnings": null
}
```

**Calculation:** Same formula as additives, but only returns max safe amount (no light/heavy).

---

#### Contract 4: Colorants List

**File:** `contracts/colorants-list.md`

**Endpoint:** `GET /api/v1/colorants`

**Query Parameters:**
- `limit`, `offset`, `search` (same as EO list)
- `category` (required): Filter by color family ("yellow", "orange", "pink", "red", "blue", "purple", "brown", "green", "black_gray")
- `sort_by` (optional): "common_name" (default)
- `sort_order` (optional): "asc", "desc" (default: asc)

**Response Schema:**
```json
{
  "colorants": [
    {
      "id": "turmeric-yellow",
      "common_name": "Turmeric",
      "botanical_name": "Curcuma longa",
      "category": "yellow",
      "usage": "1/32 tsp (yellow) to 1 tsp (orange) PPO",
      "method": "Add to lye or at trace, premix in oil",
      "color_range": "Pale yellow to burnt orange",
      "warnings": "Does not disperse in water"
    }
  ],
  "total_count": 14,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

**Note:** Colorants are informational (no automatic calculation - usage is descriptive).

---

#### Contract 5: Enhanced Calculate Endpoint

**File:** `contracts/calculate-enhanced.md`

**Endpoint:** `POST /api/v1/calculate` (EXTENDED)

**New Request Fields:**
```json
{
  "oils": [...],  // existing
  "water_percent": 38.0,  // existing
  "superfat_percent": 5.0,  // existing
  "batch_size_g": 500.0,  // existing

  // NEW: Additive selections
  "additives": [
    {
      "additive_id": "honey",
      "usage_level": "standard"  // or "light", "heavy", or numeric percentage
    },
    {
      "additive_id": "kaolin-clay",
      "usage_level": 1.5  // explicit percentage
    }
  ],

  // NEW: Essential oil selections
  "essential_oils": [
    {
      "essential_oil_id": "lavender-english",
      "usage_percent": 2.5  // explicit percentage (must be <= max_usage_rate_pct)
    }
  ]
}
```

**Enhanced Response:**
```json
{
  "recipe": {...},  // existing recipe calculation
  "additives_calculated": [
    {
      "additive_id": "honey",
      "common_name": "Honey",
      "usage_level": "standard",
      "usage_percent": 2.0,
      "amount_g": 10.0,
      "amount_oz": 0.35,
      "when_to_add": "to warm oils before mixing lye",
      "warnings": ["Can cause soap to accelerate trace"]
    }
  ],
  "essential_oils_calculated": [
    {
      "essential_oil_id": "lavender-english",
      "common_name": "Lavender (English)",
      "usage_percent": 2.5,
      "amount_g": 12.5,
      "amount_oz": 0.44,
      "max_usage_rate_pct": 3.0,
      "within_safe_limits": true
    }
  ]
}
```

**Validation Logic:**
```python
def validate_additive_selection(additive_id: str, usage_level: str | float, batch_size_g: float):
    additive = get_additive(additive_id)

    if isinstance(usage_level, str):
        # Map level to percentage
        levels = {
            "light": additive.typical_usage_min_percent,
            "standard": additive.usage_rate_standard_percent,
            "heavy": additive.typical_usage_max_percent
        }
        usage_pct = levels[usage_level]
    else:
        usage_pct = usage_level

    # Validate against max usage
    if usage_pct > additive.typical_usage_max_percent:
        warnings.append(f"Usage {usage_pct}% exceeds maximum {additive.typical_usage_max_percent}%")

    return calculate_amount(batch_size_g, usage_pct)
```

---

### 1.3 Quickstart Documentation (`quickstart.md`)

**File:** `specs/004-additive-calculator/quickstart.md`

#### Test Scenario 1: Calculate Honey Amount for 500g Batch

**Objective:** Get usage recommendations for honey in a 500g batch.

**Request:**
```bash
curl "http://localhost:8000/api/v1/additives/honey/recommend?batch_size_g=500"
```

**Expected Response:**
```json
{
  "additive_id": "honey",
  "common_name": "Honey",
  "batch_size_g": 500.0,
  "recommendations": {
    "light": {"usage_percent": 1.0, "amount_g": 5.0, "amount_oz": 0.18},
    "standard": {"usage_percent": 2.0, "amount_g": 10.0, "amount_oz": 0.35},
    "heavy": {"usage_percent": 3.0, "amount_g": 15.0, "amount_oz": 0.53}
  },
  "usage_guidance": {
    "when_to_add": "to warm oils before mixing lye",
    "preparation_instructions": "Warm slightly to ensure liquidity",
    "mixing_tips": "Add to oils, stir well, then add lye solution"
  },
  "warnings": [
    "Can cause soap to accelerate trace",
    "May cause overheating in large batches"
  ]
}
```

**Validation:**
- ✅ Light amount: 5.0g (1% of 500g)
- ✅ Standard amount: 10.0g (2% of 500g)
- ✅ Heavy amount: 15.0g (3% of 500g)
- ✅ Warnings present (accelerates_trace=true, causes_overheating=true)

---

#### Test Scenario 2: Get Usage Recommendations for Sodium Lactate

**Objective:** Retrieve usage guidance for sodium lactate (hardener).

**Request:**
```bash
curl "http://localhost:8000/api/v1/additives/sodium-lactate/recommend?batch_size_g=1000"
```

**Expected Response:**
```json
{
  "additive_id": "sodium-lactate",
  "common_name": "Sodium Lactate",
  "batch_size_g": 1000.0,
  "recommendations": {
    "light": {"usage_percent": 0.5, "amount_g": 5.0, "amount_oz": 0.18},
    "standard": {"usage_percent": 1.0, "amount_g": 10.0, "amount_oz": 0.35},
    "heavy": {"usage_percent": 1.5, "amount_g": 15.0, "amount_oz": 0.53}
  },
  "usage_guidance": {
    "when_to_add": "to oils before mixing lye",
    "preparation_instructions": "Measure carefully",
    "mixing_tips": "Add to oils and stir well"
  },
  "warnings": [
    "Can make soap crumbly if you use too much"
  ]
}
```

**Validation:**
- ✅ Standard amount: 10.0g (1% of 1000g)
- ✅ Warning about over-usage present

---

#### Test Scenario 3: Calculate Essential Oil Blend

**Objective:** Get safe usage amounts for lavender EO in 500g batch.

**Request:**
```bash
curl "http://localhost:8000/api/v1/essential-oils/lavender-english/recommend?batch_size_g=500"
```

**Expected Response:**
```json
{
  "essential_oil_id": "lavender-english",
  "common_name": "Lavender (English)",
  "batch_size_g": 500.0,
  "max_safe_amount": {
    "usage_percent": 3.0,
    "amount_g": 15.0,
    "amount_oz": 0.53
  },
  "scent_profile": "Sweet, herbaceous, and floral",
  "blending_guidance": {
    "note": "Middle",
    "blends_well_with": ["Bergamot", "Chamomile", "Geranium", "Grapefruit"]
  },
  "warnings": null
}
```

**Validation:**
- ✅ Max safe amount: 15.0g (3% of 500g)
- ✅ Blending suggestions provided
- ✅ No warnings for lavender

---

#### Test Scenario 4: Warning for Trace-Accelerating Additive

**Objective:** Verify warning system triggers for lemongrass EO.

**Request:**
```bash
curl "http://localhost:8000/api/v1/essential-oils/lemongrass/recommend?batch_size_g=500"
```

**Expected Response:**
```json
{
  "essential_oil_id": "lemongrass",
  "common_name": "Lemongrass",
  "batch_size_g": 500.0,
  "max_safe_amount": {
    "usage_percent": 1.0,
    "amount_g": 5.0,
    "amount_oz": 0.18
  },
  "scent_profile": "Lush and green citrus",
  "blending_guidance": {
    "note": "Top",
    "blends_well_with": ["Black Pepper", "Cedarwood", "Citronella"]
  },
  "warnings": "Can cause soap to trace quickly"
}
```

**Validation:**
- ✅ Low max usage rate (1.0%)
- ✅ Warning present about trace acceleration

---

## Phase 2: Implementation Strategy

### 2.1 Database Schema Implementation

#### Migration 1: Extend Additives Table

**File:** `alembic/versions/YYYYMMDD_HHMM_extend_additives_table.py`

**Operations:**
```python
def upgrade():
    op.add_column('additives', sa.Column('usage_rate_standard_percent', sa.Float(), nullable=True))
    op.add_column('additives', sa.Column('when_to_add', sa.String(200), nullable=True))
    op.add_column('additives', sa.Column('preparation_instructions', sa.Text(), nullable=True))
    op.add_column('additives', sa.Column('mixing_tips', sa.Text(), nullable=True))
    op.add_column('additives', sa.Column('category', sa.String(50), nullable=True))
    op.add_column('additives', sa.Column('accelerates_trace', sa.Boolean(), nullable=True, default=False))
    op.add_column('additives', sa.Column('causes_overheating', sa.Boolean(), nullable=True, default=False))
    op.add_column('additives', sa.Column('can_be_scratchy', sa.Boolean(), nullable=True, default=False))
    op.add_column('additives', sa.Column('turns_brown', sa.Boolean(), nullable=True, default=False))

    # Create index on category for filtering
    op.create_index('ix_additives_category', 'additives', ['category'])

def downgrade():
    op.drop_index('ix_additives_category', table_name='additives')
    op.drop_column('additives', 'turns_brown')
    op.drop_column('additives', 'can_be_scratchy')
    op.drop_column('additives', 'causes_overheating')
    op.drop_column('additives', 'accelerates_trace')
    op.drop_column('additives', 'category')
    op.drop_column('additives', 'mixing_tips')
    op.drop_column('additives', 'preparation_instructions')
    op.drop_column('additives', 'when_to_add')
    op.drop_column('additives', 'usage_rate_standard_percent')
```

**Backfill Strategy:**
```python
# After migration, run import script to populate new fields
# Existing rows will have NULL values until import
```

---

#### Migration 2: Create Essential Oils Table

**File:** `alembic/versions/YYYYMMDD_HHMM_create_essential_oils_table.py`

**Operations:**
```python
def upgrade():
    op.create_table(
        'essential_oils',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('common_name', sa.String(100), nullable=False),
        sa.Column('botanical_name', sa.String(200), nullable=False),
        sa.Column('max_usage_rate_pct', sa.Float(), nullable=False),
        sa.Column('scent_profile', sa.Text(), nullable=False),
        sa.Column('usage_notes', sa.Text(), nullable=True),
        sa.Column('blends_with', postgresql.JSONB(), nullable=True),
        sa.Column('note', sa.String(20), nullable=False),  # Top/Middle/Base
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('warnings', sa.Text(), nullable=True),
        sa.Column('color_effect', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_essential_oils_common_name', 'essential_oils', ['common_name'])
    op.create_index('ix_essential_oils_category', 'essential_oils', ['category'])
    op.create_index('ix_essential_oils_note', 'essential_oils', ['note'])

def downgrade():
    op.drop_index('ix_essential_oils_note', table_name='essential_oils')
    op.drop_index('ix_essential_oils_category', table_name='essential_oils')
    op.drop_index('ix_essential_oils_common_name', table_name='essential_oils')
    op.drop_table('essential_oils')
```

---

#### Migration 3: Create Colorants Table

**File:** `alembic/versions/YYYYMMDD_HHMM_create_colorants_table.py`

**Operations:**
```python
def upgrade():
    op.create_table(
        'colorants',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('common_name', sa.String(100), nullable=False),
        sa.Column('botanical_name', sa.String(200), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),  # color family
        sa.Column('usage', sa.String(200), nullable=False),
        sa.Column('method', sa.Text(), nullable=False),
        sa.Column('color_range', sa.String(200), nullable=False),
        sa.Column('warnings', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_colorants_category', 'colorants', ['category'])
    op.create_index('ix_colorants_common_name', 'colorants', ['common_name'])

def downgrade():
    op.drop_index('ix_colorants_common_name', table_name='colorants')
    op.drop_index('ix_colorants_category', table_name='colorants')
    op.drop_table('colorants')
```

---

### 2.2 Import Scripts

#### Script 1: Import Additives (Extended)

**File:** `scripts/import_additives_extended.py`

**Purpose:** Import 19 additives from `additives-usage-reference.json` with new calculator fields.

**Logic:**
```python
import json
from pathlib import Path
from app.db.base import SessionLocal
from app.models.additive import Additive

def parse_usage_percentage(usage_str: str) -> tuple[float, float, float]:
    """Parse usage string like '1-3%' or '~2%' into min/standard/max."""
    # Implementation: regex parsing of percentage ranges
    # Return (min_pct, standard_pct, max_pct)
    pass

def map_warnings(item: dict) -> dict[str, bool]:
    """Extract warning flags from notes/warnings."""
    warnings_text = item.get("warnings", "").lower()
    return {
        "accelerates_trace": "accelerate" in warnings_text,
        "causes_overheating": "overheat" in warnings_text,
        "can_be_scratchy": "scratch" in warnings_text,
        "turns_brown": "brown" in warnings_text or "black" in warnings_text
    }

def import_additives():
    json_path = Path("working/user-feedback/additive-calculator-feature-request/additives-usage-reference.json")
    data = json.loads(json_path.read_text())

    db = SessionLocal()
    try:
        for item in data["additives_reference"]:
            min_pct, standard_pct, max_pct = parse_usage_percentage(item["usage_rate_percentage"])
            warning_flags = map_warnings(item)

            additive = Additive(
                id=item["name"].lower().replace(" ", "-"),
                common_name=item["name"],
                inci_name=item.get("inci_name", item["name"]),  # fallback to common name
                typical_usage_min_percent=min_pct,
                typical_usage_max_percent=max_pct,
                usage_rate_standard_percent=standard_pct,
                when_to_add=item["how_to_add"],
                preparation_instructions=item.get("preparation", ""),
                mixing_tips=item.get("notes", ""),
                category=item["category"],
                accelerates_trace=warning_flags["accelerates_trace"],
                causes_overheating=warning_flags["causes_overheating"],
                can_be_scratchy=warning_flags["can_be_scratchy"],
                turns_brown=warning_flags["turns_brown"],
                quality_effects={},  # TODO: populate from research
                confidence_level="high",  # supplier-validated data
                verified_by_mga=False,  # not yet empirically tested
                safety_warnings={"raw": item.get("warnings")}
            )
            db.merge(additive)  # upsert (insert or update)

        db.commit()
        print(f"Imported {len(data['additives_reference'])} additives")
    finally:
        db.close()

if __name__ == "__main__":
    import_additives()
```

**Test Strategy:**
- Unit test: Parse usage percentages correctly
- Unit test: Extract warning flags from text
- Integration test: Import creates/updates database rows
- Integration test: Verify all 19 additives loaded

---

#### Script 2: Import Essential Oils

**File:** `scripts/import_essential_oils.py`

**Purpose:** Import 24 essential oils from `essential-oils-usage-reference.json`.

**Logic:**
```python
import json
from pathlib import Path
from app.db.base import SessionLocal
from app.models.essential_oil import EssentialOil

def import_essential_oils():
    json_path = Path("working/user-feedback/essential-oils-usage-reference.json")
    data = json.loads(json_path.read_text())

    db = SessionLocal()
    try:
        for item in data["essential_oils_reference"]:
            eo = EssentialOil(
                id=item["name"].lower().replace(" ", "-").replace("(", "").replace(")", ""),
                common_name=item["name"],
                botanical_name=item["botanical_name"],
                max_usage_rate_pct=item["max_usage_rate_pct"],
                scent_profile=item["scent_profile"],
                usage_notes=item["usage_notes"],
                blends_with=item["blends_with"],
                note=item["note"],
                category=item["category"],
                warnings=item.get("warnings"),
                color_effect=item.get("color_effect")
            )
            db.merge(eo)

        db.commit()
        print(f"Imported {len(data['essential_oils_reference'])} essential oils")
    finally:
        db.close()

if __name__ == "__main__":
    import_essential_oils()
```

**Test Strategy:**
- Integration test: Import creates database rows
- Integration test: Verify all 24 EOs loaded
- Integration test: Validate max_usage_rate_pct within 0.025%-3% range

---

#### Script 3: Import Colorants

**File:** `scripts/import_colorants.py`

**Purpose:** Import 79 colorants from `natural-colorants-reference.json`.

**Logic:**
```python
import json
from pathlib import Path
from app.db.base import SessionLocal
from app.models.colorant import Colorant

def import_colorants():
    json_path = Path("working/user-feedback/natural-colorants-reference.json")
    data = json.loads(json_path.read_text())

    db = SessionLocal()
    try:
        count = 0
        for color_family, items in data.items():
            if color_family == "usage_notes":
                continue  # skip metadata

            for item in items:
                colorant_id = f"{item['name'].lower().replace(' ', '-')}-{color_family}"
                colorant = Colorant(
                    id=colorant_id,
                    common_name=item["name"],
                    botanical_name=item.get("botanical", ""),
                    category=color_family,
                    usage=item["usage"],
                    method=item["method"],
                    color_range=item["range"],
                    warnings=item.get("warnings"),
                    notes=item.get("notes")
                )
                db.merge(colorant)
                count += 1

        db.commit()
        print(f"Imported {count} colorants across {len(data)-1} color families")
    finally:
        db.close()

if __name__ == "__main__":
    import_colorants()
```

**Test Strategy:**
- Integration test: Import creates database rows
- Integration test: Verify 79 colorants loaded (count by category)
- Integration test: Validate category values match expected color families

---

### 2.3 API Endpoint Implementation

#### Endpoint 1: Additive Recommendation

**File:** `app/api/v1/recommendations.py` (NEW)

**Implementation:**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.additive import Additive
from app.schemas.recommendation import AdditiveRecommendationResponse

router = APIRouter(prefix="/api/v1", tags=["recommendations"])

@router.get("/additives/{additive_id}/recommend", response_model=AdditiveRecommendationResponse)
async def recommend_additive_amount(
    additive_id: str,
    batch_size_g: float = Query(..., gt=0, description="Batch size in grams"),
    db: AsyncSession = Depends(get_db)
) -> AdditiveRecommendationResponse:
    """
    Calculate additive amounts for light/standard/heavy usage levels.

    Returns calculated weights in grams and ounces with usage guidance.
    """
    # Fetch additive from database
    result = await db.execute(select(Additive).where(Additive.id == additive_id))
    additive = result.scalar_one_or_none()

    if not additive:
        raise HTTPException(status_code=404, detail=f"Additive '{additive_id}' not found")

    # Calculate amounts for three levels
    def calculate(usage_pct: float) -> dict:
        amount_g = (batch_size_g * usage_pct) / 100
        amount_oz = amount_g / 28.35
        return {
            "usage_percent": usage_pct,
            "amount_g": round(amount_g, 1),
            "amount_oz": round(amount_oz, 2)
        }

    recommendations = {
        "light": calculate(additive.typical_usage_min_percent),
        "standard": calculate(additive.usage_rate_standard_percent),
        "heavy": calculate(additive.typical_usage_max_percent)
    }

    # Build warnings list
    warnings = []
    if additive.accelerates_trace:
        warnings.append("Can cause soap to accelerate trace")
    if additive.causes_overheating:
        warnings.append("May cause overheating in large batches")
    if additive.can_be_scratchy:
        warnings.append("Can be scratchy or exfoliating on skin")
    if additive.turns_brown:
        warnings.append("May turn brown or discolor in soap")

    return AdditiveRecommendationResponse(
        additive_id=additive.id,
        common_name=additive.common_name,
        batch_size_g=batch_size_g,
        recommendations=recommendations,
        usage_guidance={
            "when_to_add": additive.when_to_add,
            "preparation_instructions": additive.preparation_instructions,
            "mixing_tips": additive.mixing_tips
        },
        warnings=warnings if warnings else None
    )
```

---

#### Endpoint 2: Essential Oils List

**File:** `app/api/v1/resources.py` (EXTEND)

**Implementation:**
```python
@router.get("/essential-oils", response_model=EssentialOilListResponse)
async def list_essential_oils(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    note: Optional[Literal["Top", "Middle", "Base"]] = Query(None),
    sort_by: Literal["common_name", "max_usage_rate_pct"] = Query("common_name"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
    db: AsyncSession = Depends(get_db)
) -> EssentialOilListResponse:
    """
    List essential oils with pagination and filtering.
    """
    # Follow existing list_oils() pattern
    query = select(EssentialOil)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                EssentialOil.common_name.ilike(search_pattern),
                EssentialOil.botanical_name.ilike(search_pattern)
            )
        )

    if category:
        query = query.where(EssentialOil.category == category)

    if note:
        query = query.where(EssentialOil.note == note)

    # Count, sort, paginate (same pattern as oils)
    # ... (implementation follows existing pattern)
```

---

#### Endpoint 3: Essential Oil Recommendation

**File:** `app/api/v1/recommendations.py` (EXTEND)

**Implementation:**
```python
@router.get("/essential-oils/{eo_id}/recommend", response_model=EssentialOilRecommendationResponse)
async def recommend_essential_oil_amount(
    eo_id: str,
    batch_size_g: float = Query(..., gt=0),
    db: AsyncSession = Depends(get_db)
) -> EssentialOilRecommendationResponse:
    """
    Calculate safe essential oil amount based on max usage rate.
    """
    result = await db.execute(select(EssentialOil).where(EssentialOil.id == eo_id))
    eo = result.scalar_one_or_none()

    if not eo:
        raise HTTPException(status_code=404, detail=f"Essential oil '{eo_id}' not found")

    # Calculate max safe amount
    amount_g = (batch_size_g * eo.max_usage_rate_pct) / 100
    amount_oz = amount_g / 28.35

    return EssentialOilRecommendationResponse(
        essential_oil_id=eo.id,
        common_name=eo.common_name,
        batch_size_g=batch_size_g,
        max_safe_amount={
            "usage_percent": eo.max_usage_rate_pct,
            "amount_g": round(amount_g, 1),
            "amount_oz": round(amount_oz, 2)
        },
        scent_profile=eo.scent_profile,
        blending_guidance={
            "note": eo.note,
            "blends_well_with": eo.blends_with
        },
        warnings=eo.warnings
    )
```

---

#### Endpoint 4: Colorants List

**File:** `app/api/v1/resources.py` (EXTEND)

**Implementation:**
```python
@router.get("/colorants", response_model=ColorantListResponse)
async def list_colorants(
    category: str = Query(..., description="Color family filter (required)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    sort_by: Literal["common_name"] = Query("common_name"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
    db: AsyncSession = Depends(get_db)
) -> ColorantListResponse:
    """
    List colorants filtered by color family.

    Category must be one of: yellow, orange, pink, red, blue, purple, brown, green, black_gray
    """
    # Follow existing pattern
    query = select(Colorant).where(Colorant.category == category)

    # Search, count, sort, paginate...
```

---

#### Endpoint 5: Enhanced Calculate

**File:** `app/api/v1/calculate.py` (EXTEND)

**Implementation:**
```python
# Extend existing CalculateRequest schema
class AdditiveSelection(BaseModel):
    additive_id: str
    usage_level: str | float  # "light", "standard", "heavy", or numeric percentage

class EssentialOilSelection(BaseModel):
    essential_oil_id: str
    usage_percent: float  # explicit percentage

class CalculateRequest(BaseModel):
    # ... existing fields (oils, water_percent, superfat_percent, batch_size_g)
    additives: Optional[list[AdditiveSelection]] = None
    essential_oils: Optional[list[EssentialOilSelection]] = None

@router.post("/calculate", response_model=CalculateResponse)
async def calculate_recipe(
    request: CalculateRequest,
    db: AsyncSession = Depends(get_db)
) -> CalculateResponse:
    """
    Calculate soap recipe with optional additives and essential oils.
    """
    # ... existing recipe calculation logic

    # NEW: Process additives
    additives_calculated = []
    if request.additives:
        for selection in request.additives:
            additive = await get_additive(db, selection.additive_id)

            # Map usage level to percentage
            if isinstance(selection.usage_level, str):
                usage_pct = {
                    "light": additive.typical_usage_min_percent,
                    "standard": additive.usage_rate_standard_percent,
                    "heavy": additive.typical_usage_max_percent
                }[selection.usage_level]
            else:
                usage_pct = selection.usage_level

            # Validate and calculate
            amount_g, warnings = calculate_additive_amount(
                additive, request.batch_size_g, usage_pct
            )

            additives_calculated.append({
                "additive_id": additive.id,
                "common_name": additive.common_name,
                "usage_level": selection.usage_level,
                "usage_percent": usage_pct,
                "amount_g": amount_g,
                "when_to_add": additive.when_to_add,
                "warnings": warnings
            })

    # NEW: Process essential oils
    essential_oils_calculated = []
    if request.essential_oils:
        for selection in request.essential_oils:
            eo = await get_essential_oil(db, selection.essential_oil_id)

            # Validate usage rate
            within_safe_limits = selection.usage_percent <= eo.max_usage_rate_pct

            amount_g = (request.batch_size_g * selection.usage_percent) / 100

            essential_oils_calculated.append({
                "essential_oil_id": eo.id,
                "common_name": eo.common_name,
                "usage_percent": selection.usage_percent,
                "amount_g": amount_g,
                "max_usage_rate_pct": eo.max_usage_rate_pct,
                "within_safe_limits": within_safe_limits
            })

    return CalculateResponse(
        recipe=recipe_result,  # existing calculation
        additives_calculated=additives_calculated,
        essential_oils_calculated=essential_oils_calculated
    )
```

---

### 2.4 TDD Implementation Order

#### Phase 2.4.1: Model Layer Tests

**Order:**
1. Write `test_additive_model.py` (extend existing)
   - Test new fields (usage_rate_standard_percent, when_to_add, etc.)
   - Test warning boolean validation
   - Test category enum/validation

2. Write `test_essential_oil_model.py` (new)
   - Test field validation (max_usage_rate_pct range: 0.025-3.0)
   - Test JSONB fields (blends_with array)
   - Test note enum ("Top", "Middle", "Base")

3. Write `test_colorant_model.py` (new)
   - Test category validation (color families)
   - Test field requirements (usage, method, color_range)

**Then implement models** (pass tests)

---

#### Phase 2.4.2: Import Scripts Tests

**Order:**
4. Write `test_import_additives.py`
   - Test JSON parsing (usage percentage extraction)
   - Test warning flag mapping
   - Test database insertion (count, verify fields)
   - Test idempotency (re-import doesn't duplicate)

5. Write `test_import_eos.py`
   - Test JSON parsing (all 24 EOs)
   - Test max_usage_rate_pct validation
   - Test blends_with array population

6. Write `test_import_colorants.py`
   - Test JSON parsing (79 colorants across 9 categories)
   - Test category distribution (count per color family)

**Then implement import scripts** (pass tests)

---

#### Phase 2.4.3: API Endpoint Tests

**Order:**
7. Write `test_recommendations_api.py` (new)
   - Test additive recommendation endpoint (light/standard/heavy calculations)
   - Test essential oil recommendation endpoint (max safe amount)
   - Test error cases (404 not found, 400 invalid batch_size)

8. Write `test_resources_api.py` (extend existing)
   - Test essential oils list endpoint (pagination, search, filtering)
   - Test colorants list endpoint (category filtering required)

9. Write `test_calculate_enhanced.py` (new)
   - Test enhanced calculate with additive selections
   - Test enhanced calculate with EO selections
   - Test usage level mapping (light/standard/heavy → percentages)
   - Test warning generation (over-usage detection)

**Then implement API endpoints** (pass tests)

---

#### Phase 2.4.4: Calculation Logic Tests (Property-Based)

**Order:**
10. Write property-based tests (Hypothesis)
    - Test calculation edge cases (zero batch, extreme percentages)
    - Test usage rate boundaries (min/max validation)
    - Test warning thresholds (accelerates_trace, causes_overheating)
    - Test rounding consistency (1 decimal place)

**Then refactor calculation logic** (pass all tests)

---

### 2.5 Performance Validation

#### Load Testing Plan

**Tool:** Locust (Python-based load testing)

**Test Scenarios:**
1. **Recommendation Endpoint Load**
   - Target: `/api/v1/additives/honey/recommend?batch_size_g=500`
   - Concurrent users: 100
   - Duration: 60 seconds
   - Success criteria: p95 latency <50ms

2. **List Endpoint Load**
   - Target: `/api/v1/essential-oils?limit=50`
   - Concurrent users: 50
   - Duration: 60 seconds
   - Success criteria: p95 latency <200ms

3. **Calculate Enhanced Load**
   - Target: `/api/v1/calculate` (with 3 additives + 2 EOs)
   - Concurrent users: 50
   - Duration: 60 seconds
   - Success criteria: p95 latency <200ms

**Locust Configuration:**
```python
# locustfile.py
from locust import HttpUser, task, between

class SoapCalculatorUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def recommend_additive(self):
        self.client.get("/api/v1/additives/honey/recommend?batch_size_g=500")

    @task(2)
    def list_essential_oils(self):
        self.client.get("/api/v1/essential-oils?limit=50")

    @task(1)
    def calculate_enhanced(self):
        self.client.post("/api/v1/calculate", json={
            "oils": [{"oil_id": "olive", "percent": 70}, {"oil_id": "coconut", "percent": 30}],
            "water_percent": 38,
            "superfat_percent": 5,
            "batch_size_g": 500,
            "additives": [{"additive_id": "honey", "usage_level": "standard"}]
        })
```

**Execution:**
```bash
locust -f locustfile.py --host=http://localhost:8000
```

**Success Criteria:**
- ✅ p95 latency <50ms for recommendation endpoints
- ✅ p95 latency <200ms for list/calculate endpoints
- ✅ Error rate <0.1%
- ✅ No database connection pool exhaustion

---

### 2.6 Database Performance Optimization

#### Index Strategy

**Additives Table:**
```sql
-- Existing indexes
CREATE INDEX ix_additives_common_name ON additives(common_name);

-- New indexes
CREATE INDEX ix_additives_category ON additives(category);
```

**Essential Oils Table:**
```sql
CREATE INDEX ix_essential_oils_common_name ON essential_oils(common_name);
CREATE INDEX ix_essential_oils_category ON essential_oils(category);
CREATE INDEX ix_essential_oils_note ON essential_oils(note);
```

**Colorants Table:**
```sql
CREATE INDEX ix_colorants_category ON colorants(category);  -- PRIMARY filter
CREATE INDEX ix_colorants_common_name ON colorants(common_name);
```

**Query Performance Validation:**
```sql
-- Test recommendation query performance
EXPLAIN ANALYZE
SELECT * FROM additives WHERE id = 'honey';
-- Expected: Index Scan on additives_pkey (cost=0.15..8.17 rows=1)
-- Execution time: <1ms

-- Test list query performance
EXPLAIN ANALYZE
SELECT * FROM essential_oils
WHERE category = 'floral'
ORDER BY common_name
LIMIT 50 OFFSET 0;
-- Expected: Index Scan using ix_essential_oils_category
-- Execution time: <10ms
```

---

### 2.7 Deployment Automation

#### Ansible Playbook Updates

**File:** `ansible/playbooks/deploy-soap-calculator.yml` (EXTEND)

**New Tasks:**
```yaml
- name: Run database migrations
  shell: |
    cd /opt/soap-calculator
    source venv/bin/activate
    alembic upgrade head
  become: yes
  become_user: soap-calculator

- name: Import additives data
  shell: |
    cd /opt/soap-calculator
    source venv/bin/activate
    python scripts/import_additives_extended.py
  become: yes
  become_user: soap-calculator
  register: import_additives_result

- name: Import essential oils data
  shell: |
    cd /opt/soap-calculator
    source venv/bin/activate
    python scripts/import_essential_oils.py
  become: yes
  become_user: soap-calculator
  register: import_eos_result

- name: Import colorants data
  shell: |
    cd /opt/soap-calculator
    source venv/bin/activate
    python scripts/import_colorants.py
  become: yes
  become_user: soap-calculator
  register: import_colorants_result

- name: Display import results
  debug:
    msg: |
      Additives: {{ import_additives_result.stdout }}
      Essential Oils: {{ import_eos_result.stdout }}
      Colorants: {{ import_colorants_result.stdout }}

- name: Restart FastAPI service
  systemd:
    name: soap-calculator
    state: restarted
  become: yes
```

**Deployment Verification:**
```yaml
- name: Verify API endpoints
  uri:
    url: "http://localhost:8000/api/v1/{{ item }}"
    method: GET
    status_code: 200
  loop:
    - additives
    - essential-oils
    - colorants?category=yellow
  retries: 3
  delay: 5
```

---

## Phase 3: Risk Assessment & Mitigation

### Risk Matrix

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Data Import Errors** | HIGH | MEDIUM | Comprehensive import script tests, dry-run validation |
| **Performance Degradation** | MEDIUM | LOW | Load testing before merge, database indexes |
| **API Contract Breaking Changes** | LOW | LOW | Backward compatible extensions only |
| **Migration Rollback Failures** | MEDIUM | LOW | Test downgrade migrations, backup before deploy |
| **Incomplete Test Coverage** | HIGH | LOW | >90% coverage enforcement, property-based tests |
| **Warning System Gaps** | MEDIUM | MEDIUM | Manual review of all 122 ingredients for warnings |

### Mitigation Strategies

#### Data Import Validation

**Pre-Import Checks:**
```python
def validate_json_structure(json_data: dict) -> list[str]:
    """Validate JSON structure before import."""
    errors = []

    # Check required fields
    required_fields = ["name", "usage_rate", "category", "how_to_add"]
    for item in json_data.get("additives_reference", []):
        for field in required_fields:
            if field not in item:
                errors.append(f"Missing field '{field}' in {item.get('name', 'unknown')}")

    return errors
```

**Dry-Run Mode:**
```bash
python scripts/import_additives_extended.py --dry-run
# Output: Would import 19 additives (no database changes)
```

---

#### Performance Monitoring

**Sentry Custom Metrics:**
```python
import sentry_sdk

@router.get("/additives/{additive_id}/recommend")
async def recommend_additive_amount(...):
    with sentry_sdk.start_transaction(op="recommendation", name="additive_recommend"):
        start = time.time()

        # ... calculation logic

        duration_ms = (time.time() - start) * 1000
        sentry_sdk.metrics.distribution("recommendation.duration_ms", duration_ms)

        if duration_ms > 50:
            sentry_sdk.capture_message(
                f"Slow recommendation: {duration_ms}ms for {additive_id}",
                level="warning"
            )
```

---

## Phase 4: Success Metrics & Validation

### Definition of Done

**Feature Complete:**
- ✅ All 3 migrations applied successfully
- ✅ All 122 ingredients imported (19 additives + 24 EOs + 79 colorants)
- ✅ All 8 API endpoints functional
- ✅ Test coverage >90% (pytest-cov)
- ✅ Load testing passes (<50ms p95 for recommendations)
- ✅ OpenAPI documentation generated
- ✅ Ansible playbook updated and tested

**Quality Gates:**
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ Property-based tests passing (edge cases)
- ✅ mypy --strict type checking passing
- ✅ Ruff linting passing
- ✅ Black formatting passing

**Documentation Complete:**
- ✅ API contracts written (5 contract files)
- ✅ Quickstart guide with 4 test scenarios
- ✅ Data model documentation
- ✅ Migration guide (upgrade/downgrade procedures)

---

### Post-Deployment Validation

**Smoke Tests:**
```bash
# Test 1: List additives
curl http://localhost:8000/api/v1/additives | jq '.total_count'
# Expected: 19

# Test 2: Recommend honey amount
curl "http://localhost:8000/api/v1/additives/honey/recommend?batch_size_g=500" | jq '.recommendations.standard.amount_g'
# Expected: 10.0

# Test 3: List essential oils
curl http://localhost:8000/api/v1/essential-oils | jq '.total_count'
# Expected: 24

# Test 4: List colorants (yellow)
curl "http://localhost:8000/api/v1/colorants?category=yellow" | jq '.total_count'
# Expected: 14

# Test 5: Enhanced calculate with additives
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "oils": [{"oil_id": "olive", "percent": 70}, {"oil_id": "coconut", "percent": 30}],
    "water_percent": 38,
    "superfat_percent": 5,
    "batch_size_g": 500,
    "additives": [{"additive_id": "honey", "usage_level": "standard"}]
  }' | jq '.additives_calculated[0].amount_g'
# Expected: 10.0
```

**Performance Validation:**
```bash
# Load test (Locust)
locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=60s --headless
# Expected: p95 <50ms, error rate <0.1%
```

---

## Timeline Estimate

### Phase Breakdown

**Phase 0: Research (COMPLETED)**
- Data source validation ✅
- Constitution compliance check ✅
- Duration: Already complete

**Phase 1: Design (1 day)**
- Data model design ✅ (documented above)
- API contracts ✅ (5 contract files)
- Quickstart guide ✅ (4 test scenarios)
- Duration: 1 day

**Phase 2: Implementation (5 days)**
- Day 1: Database migrations + model extensions
- Day 2: Import scripts (3 scripts with tests)
- Day 3: API endpoints (recommendation + list)
- Day 4: Enhanced calculate endpoint
- Day 5: Integration + property-based tests

**Phase 3: Testing & Optimization (2 days)**
- Day 6: Load testing, performance optimization
- Day 7: End-to-end testing, documentation review

**Phase 4: Deployment (1 day)**
- Day 8: Ansible playbook update, staging deployment
- Production deployment after staging validation

**Total Duration:** ~9 days (1.8 weeks)

---

## Conclusion

Comprehensive implementation plan for Smart Additive Calculator feature. All design artifacts ready for task generation via `/speckit.tasks`.

**Key Strengths:**
- Extends existing patterns (low risk, high consistency)
- Simple calculation formula (high performance, low complexity)
- Validated data sources (122 ingredients from supplier/CPSR data)
- Constitution compliant (all 8 principles verified)
- TDD approach (>90% coverage target)

**Next Steps:**
1. Review this plan with stakeholders
2. Generate `tasks.md` via `/speckit.tasks` command
3. Begin Phase 2 implementation (TDD cycle)
4. Deploy to staging after passing all tests
5. Production deployment after smoke tests

**Response File Location:** `/agent-responses/20251105_095043_system-architect_additive-calculator-plan.md`

---

**System Architect Sign-Off:** Plan complete and ready for task generation.
