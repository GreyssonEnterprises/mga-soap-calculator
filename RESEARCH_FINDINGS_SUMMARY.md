# CRITICAL: Mixed Lye Formula Research Findings

**Date:** 2025-11-01
**Status:** RESOLVED - Implementation is correct, spec needs update

---

## Bottom Line

✅ **FORMULA B (IMPLEMENTATION) IS CORRECT**
❌ **FORMULA A (SPECIFICATION) IS WRONG**

**Action Required:** Update specification to match the implementation.

---

## The Verdict

### Formula B (Current Code) ✓ CORRECT
```python
# Calculate each lye type independently using its own SAP values
total_naoh = sum(oil_weight × oil_sap_naoh) × (1 - superfat)
total_koh = sum(oil_weight × oil_sap_koh) × (1 - superfat)

# Apply percentage split
naoh_amount = total_naoh × (naoh_percent / 100)
koh_amount = total_koh × (koh_percent / 100)
```

### Formula A (Spec Document) ✗ WRONG
```python
# DON'T USE THIS - treats molecular % and weight % as equivalent
weighted_sap = sum(oil_percent × oil_sap_value) / 100
total_lye = total_oil_weight × weighted_sap × (1 - superfat)
naoh_amount = total_lye × (naoh_percent / 100)  # WRONG
koh_amount = total_lye × (koh_percent / 100)    # WRONG
```

---

## Why This Matters

**Chemistry fact:** KOH molecules weigh 1.403× more than NaOH molecules
- NaOH molecular weight: 40.0 g/mol
- KOH molecular weight: 56.1 g/mol

**What "70% NaOH, 30% KOH" means:**
- 70% of the **molecules** should be NaOH
- 30% of the **molecules** should be KOH
- **NOT** 70% by weight!

**Formula A's error:** Treats weight percentage and molecular percentage as the same thing. Results in ~40% undercalculation of KOH, causing greasy, under-saponified soap.

---

## Authoritative Source

**Classic Bells (DeeAnna)** - https://classicbells.com/soap/dualLye.asp

> "The key to remember is each batch of soap requires a specific number of alkali **molecules**, whether they be KOH molecules, NaOH molecules, or a combination of both. Because each KOH molecule weighs 1.403 times more than an NaOH molecule, a soaper must allow for that weight difference so the batch gets the correct number of alkali molecules to make good soap."

DeeAnna explicitly warns against Formula A:

> "The first thought many people have when designing a dual-lye recipe is to just calculate the alkali **weight** as if the recipe was a single-lye recipe and divide this total weight in proportion to the percentages of KOH and NaOH. If you do that, however, it will not work."

---

## Professional Practice

**All professional soap calculators use Formula B:**
- LyeCalc (recommended by Classic Bells)
- SoapCalc (when used correctly for dual-lye)
- Thermal Mermaid's dual-lye calculator
- All industry-standard calculators

**Common dual-lye applications:**
- Shaving soap (90% KOH, 10% NaOH)
- Cream soap (various ratios)
- Castile bar soap (95% NaOH, 5% KOH per Anne Watson)

---

## Numerical Example of the Difference

**Recipe:** 1000g Olive Oil, 95% NaOH / 5% KOH, 5% superfat

**Using Formula A (WRONG):**
```
Total lye = 1000 × 0.1340 × 0.95 = 127.3g
NaOH = 127.3 × 0.95 = 120.9g
KOH = 127.3 × 0.05 = 6.4g
```

**Using Formula B (CORRECT):**
```
Total NaOH = 1000 × 0.1340 × 0.95 = 127.3g
Total KOH = 1000 × 0.1876 × 0.95 = 178.2g
NaOH = 127.3 × 0.95 = 120.9g
KOH = 178.2 × 0.05 = 8.9g
```

**Difference:** 8.9g vs 6.4g KOH = **39% error!**

Formula A would produce greasy soap with excess oils.

---

## Required Actions

### NO CODE CHANGES NEEDED ✓
The implementation in `src/calculators/lye_calculator.py` is chemically correct.

### SPEC UPDATE REQUIRED ✗
Update specification document to describe Formula B method.

### REFERENCE DOCS CREATED ✓
- `agent-responses/20251101_deep-research-agent_mixed-lye-formula-research.md` (full research)
- `agent-os/research/mixed-lye-calculation-methodology.md` (methodology reference)

---

## For MGA's Actual Use

MGA's recipes that use both NaOH and KOH will be calculated correctly by the current implementation. The spec just needs to be updated to document what the code actually does (which is the right thing).

**No risk to actual soap quality** - the calculator is doing the chemistry correctly.

---

## Confidence Level

**HIGH** - Multiple authoritative sources confirm:
- Classic Bells (DeeAnna) - explicit chemistry explanation
- Chemistry references (molecular weights)
- Professional calculator implementations
- Industry best practices (shaving soap, cream soap makers)
- Numerical verification with worked examples

---

**See full research:** `agent-responses/20251101_deep-research-agent_mixed-lye-formula-research.md`
**See methodology reference:** `agent-os/research/mixed-lye-calculation-methodology.md`
