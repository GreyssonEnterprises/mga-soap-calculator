# Recipe Transcription — MGA Reference Catalog

**Date:** 2026-04-18
**Branch:** `feat/capture-mga-reference-recipes`
**Working dir:** `/Volumes/owc-express/gdrive-personal/areas/rec/mga/coding/mga-soap-calculator`
**Canonical output:** `app/data/reference-recipes.yaml`
**Test:** `tests/unit/test_reference_recipes.py`

## Summary

Transcribed 24 MGA production recipes from Shale's working-docs tree on
`shale-personal-mini` into `app/data/reference-recipes.yaml`, bringing
the file from 1 recipe (Midnight Morsels, untouched) to 25 total. Added
a unit-test fixture at `tests/unit/test_reference_recipes.py` that
validates the YAML loads, IDs are unique, oils sum to 100 or document
the gap, and every oil/additive ID either resolves against
`seed-data.yaml` or is flagged in `catalog_gaps`. All 10 new tests pass.
Full unit suite: 384 passed, 126 skipped, 0 failures.

## Source files processed (remote host `shale-personal-mini`)

Base dir: `/Users/shalegreysson/Documents/gdrive-greysson/mga/projects/recipes/`

### Top-level recipes (14 captured)

| Source file                               | Recipe ID                              |
|-------------------------------------------|----------------------------------------|
| `cafe-walnut-55lb.md`                     | `cafe_walnut`                          |
| `lavender-charcoal-clay-facial-bar.md`    | `lavender_charcoal_clay_facial_bar`    |
| `lavender-dreams-55lb.md`                 | `lavender_dreams`                      |
| `lavenilla-55lb.md`                       | `lavenilla`                            |
| `lavenilla-8lb-test.md`                   | `lavenilla_8lb_test`                   |
| `mermaid-tears-55lb.md`                   | `mermaid_tears`                        |
| `mintyplotion-recipe-55lb.md`             | `mintyplotion`                         |
| `oats-and-honey-55lb.md`                  | `oats_and_honey`                       |
| `orange-spice-55lb.md`                    | `orange_spice`                         |
| `roses-and-cream-55lb.md`                 | `roses_and_cream`                      |
| `the-parlor-55lb.md`                      | `the_parlor`                           |
| `the-sentinel-55lb.md`                    | `the_sentinel`                         |
| `valhalla-calling-55lb.md`                | `valhalla_calling`                     |
| `vanvan-55lb.md`                          | `vanvan`                               |

### Midnight High Tea collection subdirectory (10 captured)

Subdir: `midnight-high-tea/`

| Source file                         | Recipe ID                                  |
|-------------------------------------|--------------------------------------------|
| `base-recipe-black-55lb.md`         | `midnight_high_tea_base_black`             |
| `constances-pomander-55lb.md`       | `midnight_high_tea_constances_pomander`    |
| `crimson-stain-55lb.md`             | `midnight_high_tea_crimson_stain`          |
| `curators-tart-55lb.md`             | `midnight_high_tea_curators_tart`          |
| `cyanide-and-lace-55lb.md`          | `midnight_high_tea_cyanide_and_lace`       |
| `gingerbread-mausoleum-55lb.md`     | `midnight_high_tea_gingerbread_mausoleum`  |
| `locked-library-55lb.md`            | `midnight_high_tea_locked_library`         |
| `mourning-truffle-55lb.md`          | `midnight_high_tea_mourning_truffle`       |
| `ophelias-garden-55lb.md`           | `midnight_high_tea_ophelias_garden`        |
| `yellow-wallpaper-55lb.md`          | `midnight_high_tea_yellow_wallpaper`       |

### Skipped (not CP/HP saponified soap)

Three source files describe sugar scrubs / surfactant bases that use
pre-made Stephenson Foaming Bath Butter (OPC) rather than a lye-based
saponification. They don't fit the current schema (no superfat, no
sap-value oils, no lye calculation):

- `grease monkey grit.md` — mechanic's sugar scrub on OPC base
- `skull-garden-scalp-scrub.md` — scalp-stimulating sugar scrub on OPC base
- `whipped-soap-base.md` — surfactant/melt-and-pour-style base recipe
  (SCI + cocamidopropyl betaine + stearic acid)

Would need a separate product-type schema (e.g., Surfactant/M&P base)
before they can be captured. Flagged for future scope.

### Also skipped (not recipes)

- `RECIPE-TEMPLATE.md`, `CLAUDE.md`, `README.md`
- `midnight-high-tea/*.md` planning/cost/timeline docs:
  `production-batch-cost-comparison.md`, `full-batch-cost-analysis.md`,
  `REALISTIC-TIMELINE.md`, `INVENTORY-ANALYSIS-PLAN.md`,
  `grimoire-page-mystery-pull.md`, `REVISED-membership-plan-with-crystals-herbs.md`,
  `fragrance-sourcing.md`, `collection-overview.md`,
  `test-batch-calculations.md`, `dark-arts-society-membership-plan.md`,
  `sourcing-options.md`, `sample-order-list.md`

## Aggregate catalog gaps (frequency across 24 new recipes)

The single most impactful gap is **beef tallow** — it appears in 23 of
24 recipes at 30.24%. This blocks accurate recipe representation in the
calculator today. Until tallow is seeded, the 23 affected recipes' oils
sum to 69.76% (or 79.76% for `the_parlor`, or 59.76% for `cafe_walnut`
with walnut+coffee oil gaps).

| Count | Gap                              | Category                                    |
|-------|----------------------------------|---------------------------------------------|
| 23    | `beef_tallow`                    | Saponifiable oil (blocks 23 recipes)        |
| 12    | `activated_charcoal`             | Additive (also used as colorant)            |
|  3    | `vanilla_oleoresin`              | Resin/fragrance (Lavenilla, Oats & Honey, Cyanide and Lace) |
|  3    | `lavender_essential_oil_english` | Essential oil                               |
|  2    | `patchouli_essential_oil`        | Essential oil                               |
|  1    | `walnut_oil`                     | Saponifiable oil (cafe_walnut)              |
|  1    | `coffee_bean_oil_roasted`        | Saponifiable oil (cafe_walnut)              |
|  1    | `tamanu_oil`                     | Saponifiable oil, trace superfat (facial bar) |
|  1    | `kokum_butter`, `mango_seed_butter`, `cupuacu_butter` | Saponifiable butters (the_parlor only) |
|  1 ea | ~40 distinct essential oils / fragrance oils | See YAML catalog_gaps per-recipe |
| many  | Micas, oxides, pigments          | Colorant table (out of scope for this file) |

Recommended catalog-expansion priorities (by recipe-unblock impact):

1. **Beef Tallow** — unblocks 23 recipes. High-impact, low-ambiguity.
2. **Activated Charcoal** as a proper additive — unblocks 12 recipes.
3. **Vanilla Oleoresin** — unblocks signature Lavenilla math. Needs a
   new category (it's a resin/fragrance, not an EO).
4. **Essential Oil catalog table** — currently MGA's EO work is entirely
   uncataloged. At minimum: lavender, peppermint, spearmint, eucalyptus,
   patchouli, frankincense, myrrh, sandalwood, bergamot, cedarwood, clove
   bud, cinnamon leaf, sweet orange + 5/10-fold.
5. **Butters for the_parlor** — kokum, mango seed, cupuacu.
6. **Specialty oils** — walnut, roasted coffee bean, tamanu.
7. **Colorants / fragrance oils** — lowest urgency; out of scope until
   the Colorant model is populated.

## Confidence grades

| Dimension     | Grade | Rationale |
|---------------|-------|-----------|
| Safety        | A     | Transcription preserves source cinnamon/clove warnings, bitter almond caution, hot-process temperature thresholds, and IFRA max-use notes. No percentages invented. |
| Effectiveness | B+    | Recipes are faithful to source docs. Two known source-doc inconsistencies preserved verbatim rather than silently corrected: (1) `lavenilla-8lb-test.md` recipe-history references a "dual clay formula" but the additive table only shows kaolin — flagged in notes. (2) `cafe-walnut-55lb.md` source lists tallow/walnut/coffee oil as "already in API" — that appears to be stale doc state; they are NOT in current seed-data.yaml. Flagged in catalog_gaps. |
| Style         | A-    | Consistent formatting with the existing Midnight Morsels entry. Descriptions capture intent, scent, and finish in 1-2 sentences. `notes:` blocks preserve critical process details (cure times, temp thresholds, layer splits, lead times for resin infusions). Some YAML comment blocks added for navigability. |

## Verification

- `python3 -c 'import yaml; d=yaml.safe_load(open("app/data/reference-recipes.yaml")); print(len(d["recipes"]))'` → **25**
- `pytest tests/unit/test_reference_recipes.py -v` → **10/10 pass**
- `pytest tests/unit` → **384 passed, 126 skipped, 0 failed**
- Version bumped via `scripts/bump-version.fish` → `2026.4.18-5` (PEP440: `2026.4.18.5`)

## Files changed

- `app/data/reference-recipes.yaml` — +1,150 lines (24 new recipe entries + header comment block)
- `tests/unit/test_reference_recipes.py` — new file, 10 tests
- `app/_version.py` — bumped to `2026.4.18-5`
- `pyproject.toml` — version = `2026.4.18.5`
- `uv.lock` — regenerated

## Next actions (for lead)

1. Review YAML entries for any recipe-specific corrections Shale/Jackie
   would catch (scent profile wording, cure-time accuracy).
2. Decide whether to unblock the 23 tallow-affected recipes by seeding
   beef tallow in `seed-data.yaml` — this is a separate PR / decision.
3. Create the Colorant model + catalog if the "try an MGA recipe"
   frontend onboarding idea advances — most recipes have rich
   color/swirl design data currently stranded in `catalog_gaps`.

## Workflow notes

- Worked from the canonical owc-express clone, not the NAS mirror
  (commits must originate from owc-express per project CLAUDE.md).
- SSH recipe pulls performed one file per invocation due to initial
  heredoc quoting failures with the space-containing filename
  `grease monkey grit.md`.
- The Python script that patched activated_charcoal into the Midnight
  High Tea `catalog_gaps` blocks is not committed (in-memory only);
  the YAML file now contains the final merged state.
