# Errata: Smart Additive Calculator

## Data Source Count Correction

**Original specification**: 122 total ingredients (19 additives + 24 EOs + 79 colorants)

**Actual data sources**: 137 total ingredients (19 additives + **39 EOs** + 79 colorants)

### Resolution

Import all 39 essential oils from `essential-oils-usage-reference.json`. The additional 15 EOs provide better coverage for soap makers and don't change the implementation strategy.

**Updated totals**:
- Additives: 19 (confirmed)
- Essential Oils: 39 (was 24)
- Colorants: 79 (confirmed)
- **Total: 137 ingredients**

### Impact

- No impact on database schema
- No impact on API design
- Import scripts will process 39 EOs instead of 24
- Smoke tests updated to expect 39 EOs instead of 24

**Date**: 2025-11-05
**Discovered During**: Phase 1 (T005 data validation)
