# Python Expert - Additive Import Scripts

**Timestamp:** 2025-11-05 13:45:00
**Task:** Create 3 import scripts for 137 ingredients
**Requestor:** Bob PAI Orchestration

## Response

Created 3 production-ready import scripts following async pattern from seed_data.py:

### 1. Import Additives (`scripts/import_additives.py`)
- **Count:** 19 additives
- **Source:** `working/user-feedback/additive-calculator-feature-request/additives-usage-reference.json`
- **Features:**
  - Parse JSON with category mapping
  - Convert usage rates (tablespoon/teaspoon → percentage)
  - Idempotent insert (skip if exists by ID)
  - Single transaction (ACID)
  - CLI with --dry-run and --verbose
  - Progress logging

### 2. Import Essential Oils (`scripts/import_essential_oils.py`)
- **Count:** 39 essential oils
- **Source:** `working/user-feedback/essential-oils-usage-reference.json`
- **Features:**
  - Parse JSON with JSONB array handling (blends_with)
  - Validate max usage rates (0.025%-3%)
  - Map scent categories
  - Idempotent insert
  - Single transaction
  - CLI interface

### 3. Import Colorants (`scripts/import_colorants.py`)
- **Count:** 79 colorants (9 color families)
- **Source:** `working/user-feedback/natural-colorants-reference.json`
- **Features:**
  - Parse nested JSON (color families as keys)
  - Map to flat colorant table
  - Category validation (yellow/orange/pink/red/blue/purple/brown/green/black_gray)
  - Idempotent insert
  - Single transaction
  - CLI interface

## Implementation Notes

### Model Creation Required
These scripts assume EssentialOil and Colorant models exist in `app/models/`. If not yet created:

```python
# app/models/essential_oil.py
class EssentialOil(Base):
    __tablename__ = "essential_oils"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    common_name: Mapped[str] = mapped_column(String(100), nullable=False)
    botanical_name: Mapped[str] = mapped_column(String(200), nullable=False)
    max_usage_rate_pct: Mapped[float] = mapped_column(Float, nullable=False)
    scent_profile: Mapped[str] = mapped_column(String(500), nullable=False)
    usage_notes: Mapped[str] = mapped_column(String(500), nullable=False)
    blends_with: Mapped[dict] = mapped_column(JSONB, nullable=False)
    note: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    warnings: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    color_effect: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=sa.func.now())

# app/models/colorant.py
class Colorant(Base):
    __tablename__ = "colorants"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    common_name: Mapped[str] = mapped_column(String(100), nullable=False)
    botanical_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    usage: Mapped[str] = mapped_column(String(200), nullable=False)
    method: Mapped[str] = mapped_column(String(500), nullable=False)
    color_range: Mapped[str] = mapped_column(String(200), nullable=False)
    warnings: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=sa.func.now())
```

### Usage Rate Conversion Logic
Additive usage rates converted from volumetric to percentage:
- 1 tablespoon PPO → ~2%
- 1 teaspoon PPO → ~1%
- 1/2 teaspoon PPO → ~0.5%
- Ranges parsed (e.g., "1-3%" → min=1.0, max=3.0)

### Execution Order
Run in any order - no dependencies between scripts:

```bash
# Dry run to verify
python scripts/import_additives.py --dry-run --verbose
python scripts/import_essential_oils.py --dry-run --verbose
python scripts/import_colorants.py --dry-run --verbose

# Execute imports
python scripts/import_additives.py
python scripts/import_essential_oils.py
python scripts/import_colorants.py
```

## Files Created

1. `/scripts/import_additives.py` - 19 additives import
2. `/scripts/import_essential_oils.py` - 39 EOs import
3. `/scripts/import_colorants.py` - 79 colorants import

## Metadata

- **Status:** Complete
- **Confidence:** High
- **Follow-up:** Create EssentialOil and Colorant model files if not exists
- **Files:** 3 import scripts created

---

## Verification

All scripts compile and parse source data successfully:
- ✓ `import_additives.py` - 210 lines, parses 19 additives
- ✓ `import_essential_oils.py` - 180 lines, parses 39 essential oils
- ✓ `import_colorants.py` - 200 lines, parses 79 colorants

**Total:** 590 lines of production-ready import code

## Execution Instructions

### 1. Create Missing Models

```bash
# Create EssentialOil model
touch app/models/essential_oil.py

# Create Colorant model
touch app/models/colorant.py

# Update __init__.py
vim app/models/__init__.py  # Add imports
```

### 2. Test Dry-Run Mode

```bash
# Activate venv
source .venv/bin/activate

# Test all imports (read-only)
python scripts/import_additives.py --dry-run --verbose
python scripts/import_essential_oils.py --dry-run --verbose
python scripts/import_colorants.py --dry-run --verbose
```

### 3. Execute Imports

```bash
# Run imports (requires database access)
python scripts/import_additives.py
python scripts/import_essential_oils.py
python scripts/import_colorants.py
```

## Script Features Summary

All scripts implement:
- ✓ Async SQLAlchemy pattern
- ✓ Idempotent inserts (skip existing by ID)
- ✓ Single transaction (ACID)
- ✓ Progress logging
- ✓ CLI with --dry-run and --verbose
- ✓ JSON parsing with validation
- ✓ Duplicate detection
- ✓ Error handling

**Status:** Ready for execution after model creation

---

**Next Steps:**
1. Create `app/models/essential_oil.py` model (see code above)
2. Create `app/models/colorant.py` model (see code above)
3. Update `app/models/__init__.py` with new imports
4. Create database migrations for new tables
5. Test dry-run mode
6. Execute import scripts
