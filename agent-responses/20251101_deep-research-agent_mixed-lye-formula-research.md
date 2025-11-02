# Deep Research Agent - Mixed Lye Formula Research

**Timestamp:** 2025-11-01
**Task:** Determine authoritative formula for mixed lye (NaOH + KOH) saponification calculations
**Requestor:** Bob (Orchestrator)
**Status:** Complete
**Confidence:** HIGH

---

## Executive Summary

**FORMULA B (Current Implementation) IS CORRECT**

The authoritative method for calculating dual-lye soap recipes requires:
1. Calculate NaOH requirement using NaOH SAP values
2. Calculate KOH requirement using KOH SAP values
3. Apply lye percentages to each total separately

**Formula A (from spec) is WRONG** - it treats lye by weight instead of by molecular count, which is chemically incorrect.

---

## The Chemistry: Why Molecular Weight Matters

### Fundamental Facts

**Molecular Weights:**
- NaOH (Sodium Hydroxide): 40.0 g/mol
- KOH (Potassium Hydroxide): 56.1 g/mol
- **Ratio: KOH weighs 1.403× more than NaOH** (56.1 ÷ 40.0 = 1.4025)

### The Critical Principle

**Soap requires a specific NUMBER OF MOLECULES of alkali, not a specific WEIGHT.**

From Classic Bells (DeeAnna, authoritative soap chemistry source):

> "The key to remember is each batch of soap requires a specific number of alkali **molecules**, whether they be KOH molecules, NaOH molecules, or a combination of both. Because each KOH molecule weighs 1.403 times more than an NaOH molecule, a soaper must allow for that weight difference so the batch gets the correct number of alkali molecules to make good soap."

Source: https://classicbells.com/soap/dualLye.asp

### Why Different SAP Values Exist

**Each oil has TWO SAP values:**
- **SAP for NaOH:** mg of NaOH needed per gram of oil
- **SAP for KOH:** mg of KOH needed per gram of oil

**The SAP values differ by exactly the molecular weight ratio (1.403):**

```
SAP_KOH = SAP_NaOH × 1.403
```

**Example (Olive Oil):**
- SAP for NaOH: 0.1340 (134.0 mg NaOH per gram)
- SAP for KOH: 0.1876 (187.6 mg KOH per gram)
- Ratio: 0.1876 ÷ 0.1340 = 1.400 ≈ 1.403 ✓

This difference exists because **KOH molecules are heavier**, so you need more grams of KOH to get the same number of molecules.

---

## The Correct Formula (Formula B - Implementation)

### Step-by-Step Process

**1. Calculate TOTAL NaOH needed (if using 100% NaOH):**
```
total_naoh = sum(oil_weight × oil_sap_naoh) × (1 - superfat)
```

**2. Calculate TOTAL KOH needed (if using 100% KOH):**
```
total_koh = sum(oil_weight × oil_sap_koh) × (1 - superfat)
```

**3. Split by desired molecular percentages:**
```
naoh_amount = total_naoh × (naoh_percent / 100)
koh_amount = total_koh × (koh_percent / 100)
```

### Why This Works

When you say "95% NaOH, 5% KOH", you mean:
- **95% of the alkali MOLECULES should be NaOH**
- **5% of the alkali MOLECULES should be KOH**

By calculating the full requirement for each lye type separately (using their respective SAP values), then splitting by percentage, you ensure the correct molecular count.

---

## The Incorrect Formula (Formula A - Spec)

### What Formula A Does Wrong

```
weighted_sap = sum(oil_percent × oil_sap_value) / 100
total_lye_needed = total_oil_weight × weighted_sap × (1 - superfat)
naoh_amount = total_lye_needed × (naoh_percent / 100)
koh_amount = total_lye_needed × (koh_percent / 100)
```

**The Fatal Flaw:** This treats lye as if weight and molecular percentage are the same.

From Classic Bells:

> "The first thought many people have when designing a dual-lye recipe is to just calculate the alkali **weight** as if the recipe was a single-lye recipe and divide this total weight in proportion to the percentages of KOH and NaOH. If you do that, however, it will not work. Your soap will either be soft and greasy from not nearly enough alkali or brittle and dangerously alkaline from too much alkali."

### Numerical Example of the Error

**Recipe:**
- 1000g Olive Oil
- 95% NaOH molecules, 5% KOH molecules
- 5% superfat

**Using Formula A (WRONG):**
```
Using NaOH SAP (0.1340):
weighted_sap = 0.1340
total_lye = 1000 × 0.1340 × 0.95 = 127.3g
naoh_amount = 127.3 × 0.95 = 120.9g NaOH
koh_amount = 127.3 × 0.05 = 6.4g KOH
```

**Using Formula B (CORRECT):**
```
total_naoh = 1000 × 0.1340 × 0.95 = 127.3g
total_koh = 1000 × 0.1876 × 0.95 = 178.2g
naoh_amount = 127.3 × 0.95 = 120.9g NaOH
koh_amount = 178.2 × 0.05 = 8.9g KOH
```

**Difference:** Formula A gives 6.4g KOH, Formula B gives 8.9g KOH - **that's a 39% error!**

With Formula A, you'd be short on alkali because you didn't account for KOH molecules being heavier. The soap would be greasy and under-saponified.

---

## Authoritative Sources

### Tier 1 (Chemistry Authority)

**1. Classic Bells (DeeAnna)**
- URL: https://classicbells.com/soap/dualLye.asp
- Authority: DeeAnna is widely recognized in the soap making community as having deep chemistry knowledge
- Method: Explicitly states molecular counting principle, provides detailed calculations
- **Direct Quote:** "Because each KOH molecule weighs 1.403 times more than an NaOH molecule, a soaper must allow for that weight difference so the batch gets the correct number of alkali molecules to make good soap."

**2. Chemistry References**
- Molecular weights confirmed across multiple chemistry sources:
  - KOH: 56.1 g/mol (Sigma-Aldrich, Wikipedia, Fisher Scientific)
  - NaOH: 40.0 g/mol (standard chemistry reference)
  - Ratio: 1.4025 (56.1 ÷ 40.0)

### Tier 2 (Soap Making Industry)

**3. From Nature With Love (FNWL)**
- URL: https://www.fromnaturewithlove.com/resources/sapon.asp
- Method: Provides both NaOH and KOH SAP values for all oils
- Explicitly states conversion: "Dividing the SAP value by 1402.50 or multiplying the KOH ratio by 40/56.1 (the ratio of the molecular weights of NaOH/KOH)"

**4. GloryBee Blog**
- URL: https://www.glorybee.com/blog/soap-making-saponification-and-sap-values
- Provides separate SAP calculations for NaOH and KOH
- Shows worked examples using different SAP values for each lye type

### Tier 3 (Calculator Implementations)

**5. LyeCalc**
- Mentioned by Classic Bells as correct implementation
- Uses separate SAP values for NaOH and KOH
- Calculates each lye requirement independently

**6. SoapCalc**
- Classic Bells tutorial shows how to "trick" SoapCalc into dual-lye calculations
- Method: Calculate recipe twice (once with all NaOH, once with all KOH), then split
- This is exactly what Formula B does programmatically

---

## Professional Practice Confirmation

### Common Dual-Lye Applications

**1. Shaving Soap:** Typically 90% KOH, 10% NaOH
- Needs the creamy lather of KOH soap
- Needs the firmness of NaOH soap
- Formula B is standard practice

**2. Cream Soap:** Various ratios of NaOH/KOH
- Thermal Mermaid (professional soap educator) uses dual-lye calculators
- All calculators use separate SAP values (Formula B approach)

**3. Castile Bar Soap:** 95% NaOH, 5% KOH (Anne Watson recommendation)
- Anne Watson's book "Castile Soapmaking" recommends this
- Classic Bells confirms this is calculated using Formula B method

---

## Test Case Validation

### Recipe Parameters
- 1000g oils (500g Olive, 500g Coconut)
- 70% NaOH molecules, 30% KOH molecules
- 5% superfat

### SAP Values
**Olive Oil:**
- NaOH: 0.1340
- KOH: 0.1876

**Coconut Oil:**
- NaOH: 0.1900
- KOH: 0.2661

### Calculation Using Formula B (CORRECT)

**Step 1: Calculate total NaOH if using 100% NaOH**
```
Olive:   500g × 0.1340 = 67.0g NaOH
Coconut: 500g × 0.1900 = 95.0g NaOH
Total:   162.0g NaOH (before superfat)
With 5% superfat: 162.0 × 0.95 = 153.9g NaOH
```

**Step 2: Calculate total KOH if using 100% KOH**
```
Olive:   500g × 0.1876 = 93.8g KOH
Coconut: 500g × 0.2661 = 133.05g KOH
Total:   226.85g KOH (before superfat)
With 5% superfat: 226.85 × 0.95 = 215.5g KOH
```

**Step 3: Apply molecular percentages**
```
NaOH amount: 153.9g × 0.70 = 107.7g NaOH
KOH amount:  215.5g × 0.30 = 64.7g KOH
```

**Result: 107.7g NaOH + 64.7g KOH**

### Verification of Molecular Percentage

To verify this gives us 70% NaOH molecules and 30% KOH molecules:

```
NaOH molecules = 107.7g ÷ 40.0 g/mol = 2.693 mol
KOH molecules = 64.7g ÷ 56.1 g/mol = 1.153 mol
Total molecules = 3.846 mol

NaOH percentage = 2.693 ÷ 3.846 = 70.0% ✓
KOH percentage = 1.153 ÷ 3.846 = 30.0% ✓
```

Perfect match! Formula B produces exactly the molecular percentages requested.

---

## Recommendation

**KEEP FORMULA B (Current Implementation)**

The implementation code is chemically correct and matches:
- Classic Bells (DeeAnna) - authoritative soap chemistry source
- Professional soap making calculators (LyeCalc, SoapCalc method)
- Industry best practices
- Fundamental chemistry principles

**UPDATE SPECIFICATION**

The spec document should be corrected to match Formula B. The spec's Formula A is based on a common misconception (treating weight and molecular percentage as equivalent) that Classic Bells explicitly warns against.

---

## Implementation Verification

### Current Code Location
`src/calculators/lye_calculator.py`

### Code Review
The current implementation correctly:
1. Uses separate `sap_naoh` and `sap_koh` properties for each oil
2. Calculates total NaOH requirement independently
3. Calculates total KOH requirement independently
4. Applies percentage splits to each total
5. Applies superfat correctly

**No code changes needed** - implementation is correct.

**Spec update needed** - documentation should match the correct chemistry.

---

## Sources Consulted

1. **Classic Bells - Dual Lye Recipe** (Tier 1 - Primary Authority)
   - https://classicbells.com/soap/dualLye.asp
   - Author: DeeAnna
   - Explicit molecular counting explanation
   - Hand calculation tutorial
   - Calculator recommendations

2. **From Nature With Love - Saponification Chart** (Tier 2)
   - https://www.fromnaturewithlove.com/resources/sapon.asp
   - SAP values for both NaOH and KOH
   - Molecular weight conversion explanation

3. **GloryBee - Saponification and SAP Values** (Tier 2)
   - https://www.glorybee.com/blog/soap-making-saponification-and-sap-values
   - Worked examples with both lye types

4. **Chemistry Sources** (Tier 1 - Molecular Weights)
   - Sigma-Aldrich, Fisher Scientific, Wikipedia
   - KOH: 56.1 g/mol
   - NaOH: 40.0 g/mol

5. **Soap Making Forums** (Tier 3 - Professional Practice)
   - SoapMakingForum.com discussions
   - Thermal Mermaid (professional educator)
   - Anne Watson (author, "Castile Soapmaking")

---

## Metadata

- **Status:** Complete
- **Confidence:** HIGH - Multiple authoritative sources agree
- **Follow-up:** Update specification to match correct formula
- **Files Modified:** None (implementation is correct)
- **Files to Update:** Specification document

---

## Chemistry Principle Summary

**For anyone who needs to understand this in the future:**

Think of it like currency exchange:
- You need 100 "alkali molecules" to make soap
- NaOH molecules "cost" 40g each
- KOH molecules "cost" 56.1g each
- If you want 70 NaOH molecules and 30 KOH molecules:
  - 70 NaOH molecules × 40g = 2800g worth of NaOH
  - 30 KOH molecules × 56.1g = 1683g worth of KOH
  - You can't just add 2800+1683 and split it 70/30 by weight
  - You have to calculate each currency separately, THEN split

Formula A tries to average the "cost" and split by weight - **wrong**.
Formula B calculates each "currency" separately - **correct**.
