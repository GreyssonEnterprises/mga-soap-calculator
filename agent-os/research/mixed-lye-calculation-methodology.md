# Mixed Lye Calculation Methodology

**Reference Document for MGA Soap Calculator**
**Last Updated:** 2025-11-01
**Research Source:** agent-responses/20251101_deep-research-agent_mixed-lye-formula-research.md

---

## Quick Reference

### The Correct Formula

For dual-lye soap (NaOH + KOH mixture):

```python
# Step 1: Calculate total NaOH needed (100% NaOH scenario)
total_naoh = sum(oil_weight × oil_sap_naoh for each oil) × (1 - superfat)

# Step 2: Calculate total KOH needed (100% KOH scenario)
total_koh = sum(oil_weight × oil_sap_koh for each oil) × (1 - superfat)

# Step 3: Apply molecular percentages
naoh_amount = total_naoh × (naoh_percent / 100)
koh_amount = total_koh × (koh_percent / 100)
```

### Why This Formula

**Chemistry Principle:** Soap requires a specific NUMBER of alkali molecules, not a specific WEIGHT.

**Molecular Weights:**
- NaOH: 40.0 g/mol
- KOH: 56.1 g/mol
- Ratio: KOH is 1.403× heavier

**Implication:** SAP values differ between NaOH and KOH by this ratio. You must calculate each lye requirement separately, then split by desired molecular percentage.

---

## Common Mistake to Avoid

**WRONG APPROACH (Formula A - treat as weight):**
```python
# DON'T DO THIS
weighted_sap = sum(oil_percent × oil_sap_value) / 100
total_lye = total_oil_weight × weighted_sap × (1 - superfat)
naoh_amount = total_lye × (naoh_percent / 100)  # WRONG
koh_amount = total_lye × (koh_percent / 100)    # WRONG
```

**Why it's wrong:** This treats molecular percentage and weight percentage as equivalent. KOH molecules are heavier, so this under-calculates KOH needs by ~40%.

**Result:** Greasy, under-saponified soap with excess oils.

---

## Authoritative Source

**Classic Bells (DeeAnna)**
https://classicbells.com/soap/dualLye.asp

> "The key to remember is each batch of soap requires a specific number of alkali **molecules**, whether they be KOH molecules, NaOH molecules, or a combination of both. Because each KOH molecule weighs 1.403 times more than an NaOH molecule, a soaper must allow for that weight difference so the batch gets the correct number of alkali molecules to make good soap."

DeeAnna is widely recognized in the professional soap making community as a chemistry authority.

---

## SAP Values

Each oil has **two** SAP values:

### Example: Olive Oil
- **SAP for NaOH:** 0.1340 (134.0 mg NaOH per gram of oil)
- **SAP for KOH:** 0.1876 (187.6 mg KOH per gram of oil)
- **Ratio:** 0.1876 ÷ 0.1340 = 1.400 ≈ 1.403

### Example: Coconut Oil
- **SAP for NaOH:** 0.1900 (190.0 mg NaOH per gram of oil)
- **SAP for KOH:** 0.2661 (266.1 mg KOH per gram of oil)
- **Ratio:** 0.2661 ÷ 0.1900 = 1.401 ≈ 1.403

The ratio is constant because it reflects the molecular weight difference.

---

## Worked Example

### Recipe
- 1000g oils (50% Olive, 50% Coconut)
- 70% NaOH molecules, 30% KOH molecules
- 5% superfat

### Calculation

**Step 1: Total NaOH (if 100% NaOH)**
```
Olive (500g):   500 × 0.1340 = 67.0g
Coconut (500g): 500 × 0.1900 = 95.0g
Total: 162.0g
With superfat: 162.0 × 0.95 = 153.9g
```

**Step 2: Total KOH (if 100% KOH)**
```
Olive (500g):   500 × 0.1876 = 93.8g
Coconut (500g): 500 × 0.2661 = 133.05g
Total: 226.85g
With superfat: 226.85 × 0.95 = 215.5g
```

**Step 3: Apply percentages**
```
NaOH: 153.9 × 0.70 = 107.7g
KOH:  215.5 × 0.30 = 64.7g
```

**Result: 107.7g NaOH + 64.7g KOH**

### Verification
```
NaOH moles: 107.7 ÷ 40.0 = 2.693 mol
KOH moles:  64.7 ÷ 56.1 = 1.153 mol
Total: 3.846 mol

NaOH %: 2.693 ÷ 3.846 = 70.0% ✓
KOH %:  1.153 ÷ 3.846 = 30.0% ✓
```

---

## Common Use Cases

### Shaving Soap
**Typical ratio:** 90% KOH, 10% NaOH
- KOH makes creamy, soluble lather
- NaOH adds firmness
- Must use correct formula for proper consistency

### Cream Soap
**Various ratios** depending on desired texture
- Professional calculators all use separate SAP values
- Formula B is industry standard

### Castile Bar Soap (Anne Watson method)
**Ratio:** 95% NaOH, 5% KOH
- Small amount of KOH reduces olive oil "slime"
- Improves bar soap texture
- Calculation must account for molecular weight difference

---

## Implementation Notes

### MGA Calculator Status
✓ **Implementation is correct** (uses Formula B)
✗ **Specification was wrong** (described Formula A)

### Code Location
`src/calculators/lye_calculator.py`

### Required Changes
- **Code:** None - implementation is chemically correct
- **Spec:** Update to describe Formula B method
- **Documentation:** Reference this methodology document

---

## References

1. **Classic Bells - Dual Lye Recipe**
   - https://classicbells.com/soap/dualLye.asp
   - Primary authority on dual-lye chemistry

2. **From Nature With Love - SAP Values**
   - https://www.fromnaturewithlove.com/resources/sapon.asp
   - Comprehensive SAP tables (both NaOH and KOH)

3. **GloryBee - Saponification Guide**
   - https://www.glorybee.com/blog/soap-making-saponification-and-sap-values
   - Worked examples and explanations

4. **Anne Watson - Castile Soapmaking**
   - Book recommendation for 95/5 NaOH/KOH castile bars

---

## For Future Developers

**If you're tempted to "simplify" this calculation:**

Don't. The separate SAP values exist for a reason. The molecular weight difference is chemistry, not preference.

**Think of it this way:**
- 100 molecules of NaOH weigh 4000g (100 × 40)
- 100 molecules of KOH weigh 5610g (100 × 56.1)
- If you need 70 NaOH + 30 KOH molecules (100 total), you need:
  - 70 × 40 = 2800g NaOH
  - 30 × 56.1 = 1683g KOH
  - Total: 4483g of lye

**You can't just take 100 "average" molecules and split 70/30 by weight.**

That's the mistake Formula A makes. Don't make it.

---

## Currency Exchange Analogy

**For non-chemists:**

Imagine you need to pay 100 units of "alkali currency" to make soap:
- NaOH molecules are like dollars ($40 each)
- KOH molecules are like euros (€56.10 each)

If you want to pay with 70 dollars and 30 euros:
- 70 dollars = 70 × $40 = $2800
- 30 euros = 30 × €56.10 = €1683

**Wrong approach:** Add $2800 + €1683 = 4483 "units", then split 70/30
**Right approach:** Calculate each currency separately, THEN combine

Formula B is the "right approach" - calculate each lye type independently using its own SAP value (exchange rate), then apply the split.

---

**End of Reference Document**
