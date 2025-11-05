# Specification: Comprehensive Oils Database Import

## Goal
Import 147 oils with complete fatty acid profiles, SAP values, INCI names, and quality metrics to establish the most comprehensive soap calculator database in the industry (53% more coverage than leading competitors).

## User Stories
- As a soap maker, I want access to 147 different oils and butters so that I can formulate with exotic, specialty, and traditional ingredients that other calculators don't support
- As a professional formulator, I want complete fatty acid profiles and INCI names for all oils so that I can create accurate ingredient labels and understand soap quality characteristics

## Specific Requirements

**Database Schema Extension**
- Existing Oil model already supports all required fields (id, common_name, inci_name, sap_value_naoh, sap_value_koh, iodine_value, ins_value, fatty_acids JSONB, quality_contributions JSONB)
- No schema migration needed - current structure at app/models/oil.py is complete
- Fatty acids structure: 8 standard fatty acids (lauric, myristic, palmitic, stearic, oleic, linoleic, linolenic, ricinoleic) as percentages
- Quality contributions structure: 7 metrics (hardness, cleansing, conditioning, bubbly_lather, creamy_lather, longevity, stability) as numeric values 0-99

**Import Script Design**
- Extend existing scripts/seed_database.py pattern for idempotent operation
- Load from working/user-feedback/oils-db-additions/complete-oils-database.json (147 oils)
- Use existing duplicate detection pattern: check Oil.id existence before insert
- Preserve existing async/await pattern with AsyncSession
- Add progress reporting: "Processing X of 147 oils..." with visual indicators
- Handle special cases: Pine Tar (no traditional fatty acids), Meadowfoam (unusual C20/C22 approximated as oleic)

**Data Validation Rules**
- SAP value ranges: NaOH 0.100-0.300, KOH 0.140-0.420 (enforce reasonable bounds)
- Fatty acids must sum to 95-100% (allow 5% tolerance for rounding and trace components)
- Quality metrics must be 0-99 range (already enforced by source data)
- Iodine values: 0-200 typical range
- INS values: 0-350 typical range
- INCI names may be empty string (not all oils have standardized INCI names)
- Reject oils with missing SAP values or completely empty fatty acid profiles

**INCI Name Handling**
- Import existing INCI names from JSON as-is (some oils have complete INCI names)
- Empty INCI names are acceptable (will be populated in future enhancement)
- No INCI validation at import time - accept whatever is in source data
- Priority INCI completion (Tier 1 & 2 oils) is out of scope for this import

**Idempotent Import Strategy**
- Use existing pattern: SELECT to check existence by Oil.id, skip if found
- Log both added and skipped counts for transparency
- Support multiple executions without duplication or errors
- Provide clear output: "X oils added, Y oils skipped (already exist)"
- No updates to existing oils - import is append-only for safety

**Data Integrity Validation**
- Pre-import validation: parse JSON, check structure, validate all 147 entries parse correctly
- Per-oil validation during import: check SAP ranges, fatty acid sum, required fields present
- Post-import verification: count total oils in database, verify sample oils have correct data
- Rollback on validation failure: use database transaction to ensure all-or-nothing import
- Log validation failures with specific oil name and reason for troubleshooting

**Performance Targets**
- Total import time <5 minutes for all 147 oils (33 seconds average = ~0.3s per oil)
- Database connection pooling via existing async engine
- Batch commit strategy: commit all oils in single transaction for ACID compliance
- Progress logging every 10 oils to show activity without overwhelming output

**Error Handling**
- Catch JSON parse errors: report file corruption or format issues
- Catch validation errors: log specific oil and validation rule violation
- Catch database errors: report connection issues, constraint violations
- Provide actionable error messages: include oil name, field name, expected vs actual values
- Exit with non-zero status code on failure for CI/CD integration

## Visual Design
No visual design assets - this is a backend database import specification.

## Existing Code to Leverage

**scripts/seed_database.py**
- Async database seeding pattern with progress reporting
- Idempotent duplicate detection: SELECT then conditional INSERT
- Visual progress indicators: emoji-based status (✓ added, ⏭ skipped)
- Clean output formatting with counts and summaries
- Transaction management with async session commit

**scripts/seed_data.py**
- Data structure patterns for OIL_SEED_DATA list format
- Example fatty acid profile structures
- Example quality contributions structures
- Pattern for organizing seed data as Python constants

**app/models/oil.py**
- Complete Oil model with all required fields
- JSONB storage for fatty_acids and quality_contributions
- Timestamp management with server_default and triggers
- Existing schema requires no changes

**app/core/config.py (implied)**
- DATABASE_URL configuration via settings
- Async engine creation pattern

**existing idempotent test pattern in scripts/test_seed_idempotent.py**
- Test methodology for verifying safe re-execution
- Validation that duplicate detection prevents errors
- Pattern for testing database state after multiple runs

## Out of Scope
- INCI name completion for oils with empty INCI fields (future enhancement)
- Saponified INCI name generation (separate feature - requires chemical name transformation)
- Extended fatty acid support for C20/C22 (Meadowfoam, Mustard oil special cases)
- Pine Tar special handling flags (accept as-is with zero fatty acids)
- Updating existing oils already in database (import is append-only)
- Database migration creation (schema already complete, no changes needed)
- API endpoint modifications (oils endpoint already supports all fields)
- Frontend updates to display new oils (automatic via existing /v1/oils endpoint)
- Data quality improvements beyond source data (accept JSON as authoritative)
- Manual INCI research or validation (use source data as-is)
