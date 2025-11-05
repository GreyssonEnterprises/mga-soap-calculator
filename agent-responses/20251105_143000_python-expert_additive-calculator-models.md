# Python Expert - Additive Calculator Database Models
**Timestamp:** 2025-11-05T14:30:00Z
**Task:** Create 3 database models for Feature 004 Smart Additive Calculator
**Requestor:** Bob

## Response

Created three SQLAlchemy 2.0 models following existing Oil model patterns with proper typing and PostgreSQL features.

### 1. Extended Additive Model

**File:** `app/models/additive.py`

**Added Fields:**
- `usage_rate_min_pct: Mapped[Optional[Decimal]]` - Light usage percentage (Numeric 5,2)
- `usage_rate_max_pct: Mapped[Optional[Decimal]]` - Heavy usage percentage (Numeric 5,2)
- `usage_rate_standard_pct: Mapped[Optional[Decimal]]` - Standard recommended percentage (Numeric 5,2)
- `when_to_add: Mapped[Optional[str]]` - Timing guidance (String 200)
- `preparation_instructions: Mapped[Optional[str]]` - Prep requirements (String 500)
- `category: Mapped[Optional[str]]` - Additive category (String 50)
- `warnings: Mapped[Optional[dict]]` - Specific warnings as JSONB

**Design Decisions:**
- Used `Numeric(5, 2)` for precise percentage calculations (handles 0.25% to 999.99%)
- All new fields nullable to support gradual data population
- JSONB for warnings to store structured data: `{accelerates_trace: true, causes_overheating: false}`
- Maintains existing fields for backward compatibility

### 2. EssentialOil Model

**File:** `app/models/essential_oil.py`

**Complete Model for 39 Essential Oils:**
```python
class EssentialOil(Base):
    id: str                              # Primary key
    common_name: str                     # "Lavender", "Peppermint"
    botanical_name: Optional[str]        # "Lavandula angustifolia"
    inci_name: Optional[str]             # INCI standard name
    max_usage_rate_pct: Decimal          # Numeric(5, 3) for 0.025% to 3.000%
    scent_profile: Optional[str]         # Descriptive scent
    note: Optional[str]                  # top/middle/base
    blends_with: Optional[list]          # ARRAY(String) of oil IDs
    category: Optional[str]              # citrus, floral, woody, etc.
    warnings: Optional[list]             # ARRAY(String) for multiple warnings
    created_at: datetime
    updated_at: datetime
```

**Design Decisions:**
- `Numeric(5, 3)` for precise essential oil percentages (supports 0.025% like citrus oils)
- PostgreSQL ARRAY for blends_with - efficient storage of multiple IDs
- PostgreSQL ARRAY for warnings - supports multiple independent warnings
- Follows Oil model's timestamp and __repr__ patterns exactly

### 3. Colorant Model

**File:** `app/models/colorant.py`

**Complete Model for 79 Natural Colorants:**
```python
class Colorant(Base):
    id: str                              # Primary key
    name: str                            # "Turmeric", "Activated Charcoal"
    botanical_name: Optional[str]        # Scientific name if applicable
    color_category: str                  # yellow, orange, pink, red, etc.
    usage_rate: Optional[str]            # "1-3 tsp per pound"
    method: Optional[str]                # "infuse in oil", "add at trace"
    color_range_description: Optional[str] # "pale yellow to burnt orange"
    warnings: Optional[str]              # "fades with time, stains"
    notes: Optional[str]                 # Additional guidance
    created_at: datetime
    updated_at: datetime
```

**Design Decisions:**
- `usage_rate` as String for flexibility - colorants use diverse measurement units
- `method` as String to accommodate various application techniques
- Simple String for warnings (not JSONB) - colorant warnings are descriptive text
- `color_category` required field for filtering by color family

## Pattern Compliance

All three models follow established codebase patterns:

**SQLAlchemy 2.0 Typed Mapping:**
- ✅ `Mapped[type]` annotations throughout
- ✅ `mapped_column()` with explicit parameters
- ✅ Type hints with Optional where nullable

**PostgreSQL Features:**
- ✅ `JSONB` for structured data (Additive.warnings)
- ✅ `ARRAY(String)` for lists (EssentialOil.blends_with, EssentialOil.warnings)
- ✅ `Numeric` for precise decimal calculations

**Timestamp Management:**
- ✅ `created_at` with `server_default=sa.func.now()`
- ✅ `updated_at` with `server_default=sa.func.now()`
- ✅ Both use `DateTime(timezone=True)` for UTC
- ✅ Comments indicate PostgreSQL trigger for auto-update

**Naming Conventions:**
- ✅ Snake_case for all column names
- ✅ Descriptive field names matching spec
- ✅ Consistent Optional usage for nullable fields

**Documentation:**
- ✅ Module docstrings explaining purpose
- ✅ Class docstrings with context
- ✅ Column comments for complex fields
- ✅ `__repr__` methods for debugging

## Next Steps

**Required:**
1. Create Alembic migration: `alembic revision --autogenerate -m "Add smart additive calculator models"`
2. Review and apply migration: `alembic upgrade head`
3. Seed data from reference JSON files:
   - `additives-usage-reference.json` (populate new Additive fields)
   - `essential-oils-usage-reference.json` (39 essential oils)
   - `natural-colorants-reference.json` (79 colorants)

**Validation:**
1. Verify models import cleanly: `python -c "from app.models.essential_oil import EssentialOil; from app.models.colorant import Colorant"`
2. Test database schema creation in dev environment
3. Verify ARRAY and JSONB columns work with PostgreSQL

## Metadata

- Status: Complete
- Confidence: High
- Follow-up: Yes (migration and seeding required)
- Files:
  - `app/models/additive.py` (extended)
  - `app/models/essential_oil.py` (new)
  - `app/models/colorant.py` (new)
