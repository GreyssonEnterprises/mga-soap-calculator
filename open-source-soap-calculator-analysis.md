# Open Source Soap Calculator Analysis

**Analysis Date:** October 24, 2025
**Purpose:** Systematic review of existing soap calculators to inform MGA soap calculator development

---

## Executive Summary

After reviewing 3 open-source projects and 3 commercial platforms, **NONE of the existing solutions support custom non-fat additives with impact on soap quality metrics**. All calculators limit quality calculations to oil/fat blends only. The most comprehensive open-source solution (Soapee) was decommissioned in 2024 but source code is available.

**Key Finding:** Building additive support will require:
1. Creating an additives database with quality impact values (empirical data needed)
2. Extending calculation logic beyond weighted oil averages
3. Research into how additives (clays, salts, botanicals) affect soap properties

---

## Open Source Projects

### 1. Soapee (nazar/soapee.open)
- **Repository:** https://github.com/nazar/soapee.open
- **Status:** Decommissioned April 30, 2024, archived repository
- **Tech Stack:** JavaScript (97.8%), Node.js, React, PostgreSQL
- **License:** AGPLv3
- **Stars:** 13 | **Forks:** 7

#### Features
✅ **Comprehensive saponification calculator**
✅ **Soap recipe database** with user accounts
✅ **Quality metrics:** Hardness, Cleansing, Conditioning, Bubbly, Creamy
✅ **Fatty acid profiles:** Lauric, Myristic, Palmitic, Stearic, Ricinoleic, Oleic, Linoleic, Linolenic
✅ **Iodine & INS values**
✅ **NaOH and KOH support**
✅ **Recipe saving and sharing**
✅ **Community features**
✅ **Docker-based development environment**

❌ **No additive support** (oils/fats only)
❌ **No cost calculator**
❌ **Requires full database setup**

#### Architecture
- **Backend:** Node.js API (`api/` directory)
- **Frontend:** React web client (`client-web/`)
- **Database:** PostgreSQL with migrations (`database/`)
- **Deployment:** Docker Compose setup included
- **Testing:** E2E tests (`e2e/`)

#### Assessment
**Most comprehensive open-source solution found.** Full-featured application with proper architecture, user management, and recipe database. Code quality appears professional. Archived but still usable as reference or starting point.

**Note:** Author explicitly states code is outdated and warns against public hosting due to security concerns. Best used for local/private instances.

---

### 2. Sporiff/soap-calculator
- **Repository:** https://github.com/Sporiff/soap-calculator
- **Status:** Archived July 16, 2023 (read-only)
- **Tech Stack:** Python 100%, GTK
- **License:** GPL-3.0
- **Stars:** 1 | **Forks:** 1

#### Features
✅ **Basic GTK desktop application**
✅ **Python-based saponification calculator**
✅ **Simple interface**

❌ **Very minimal functionality** (basic SAP calculations only)
❌ **No quality metrics**
❌ **No database of oils** (appears to be hardcoded)
❌ **No web interface**
❌ **Archived/abandoned**

#### Assessment
**Minimal reference value.** This is essentially a proof-of-concept desktop calculator. No advanced features, no quality metrics, no additive support. Not suitable as a foundation for professional development.

---

### 3. msbeaule/soap-calculator
- **Repository:** https://github.com/msbeaule/soap-calculator
- **Status:** Active (last commit April 2023)
- **Tech Stack:** JavaScript (simple static site)
- **License:** None specified
- **Live Demo:** https://msbeaule.github.io/soap-calculator/

#### Features
✅ **Simple JavaScript calculator**
✅ **Basic SAP calculations**
✅ **Supports 5 oils:** Olive, Coconut, Castor, Hemp, Babassu
✅ **Superfat percentage**
✅ **Web-based (GitHub Pages)**

❌ **No quality metrics**
❌ **No fatty acid profiles**
❌ **Limited oil database** (only 5 oils, sunflower and apricot noted as TODO)
❌ **No additives support**
❌ **No recipe saving**
❌ **Very basic UI**

#### Assessment
**Beginner-level implementation.** Good for understanding basic SAP calculations but lacks professional features. Could serve as educational reference for calculation logic but not suitable for production use.

---

## Commercial/Online Platforms

### 1. SoapMaking Friend
- **URL:** https://www.soapmakingfriend.com/
- **Platform:** Web + iOS + Android apps (cloud-synced)
- **Pricing:** Free (2 recipes, 1 batch) | Premium $5.99/month (unlimited)

#### Features
✅ **Comprehensive recipe builder** with all necessary calculators
✅ **Large database of oils, fats, waxes**
✅ **Custom additives support** *(likely just notes, not calculations)*
✅ **Ability to add custom ingredients**
✅ **Real-time property updates** as recipe changes
✅ **Recipe notes and images**
✅ **Print-friendly format**
✅ **Inventory management** (track purchases, suppliers, stock)
✅ **Batch management** (portions, packaging, labor)
✅ **Cost analysis**
✅ **Recipe folders and filtering**
✅ **Recipe replication**
✅ **Community features** (share recipes, forums)
✅ **Cross-platform sync**

❓ **Unclear if additives affect quality metrics** (likely just tracking, not calculation)

#### Assessment
**Most feature-rich commercial platform.** Excellent inventory and business management tools. However, from description alone, cannot confirm if additives actually impact quality calculations or if they're just tracked in notes.

---

### 2. Soap Metrics
- **URL:** https://soapmetrics.com/
- **Pricing:** Free tier | Premium $3.99/month

#### Features
✅ **Professional soap calculator** with 300+ oils & additives
✅ **Real-time updates & feedback**
✅ **100% real scientific calculations** (claimed)
✅ **NaOH, KOH, and hybrid formulations**
✅ **Fatty acid profiles**
✅ **Quality metrics:** Hardness, Cleansing, Conditioning, Bubbly Lather, Creamy Lather, Longevity, Stability, Iodine, INS
✅ **Additive support** (powders, liquids, toppings)
✅ **Fragrance calculator** (percentage or fixed amount)
✅ **Cost calculator** with detailed business analysis
✅ **Packaging costs, time tracking, platform fees**
✅ **Profit margin calculator**
✅ **Recipe export** (PDF, JSON)
✅ **Recipe storage** (unlimited with premium)
✅ **Soap community** (share recipes)
✅ **Step-by-step recipe instructions** (premium)

#### Notable Features
- **Additives are type-categorized:** Powder additives, liquids, toppings
- **Additives can be added by percentage of oils or fixed weight**
- **Multiple calculation methods** for water (water as % of oils, lye concentration, water:lye ratio)
- **Superfat method options** (lye discount standard vs other methods)
- **Comprehensive cost calculator** including time valuation and sales platform fees

❓ **CRITICAL QUESTION:** Do additives affect quality metrics or just tracked for cost/recipe recording?

#### Assessment
**Most technically sophisticated commercial platform.** Claims "100% real scientific calculations" and explicitly supports additives with different input methods. However, from interface alone, **cannot confirm if additive amounts affect the quality bars** (Hardness, Cleansing, Conditioning, etc.) or if they're only tracked for recipe completeness and costing.

**This is the key question for our requirements.**

---

### 3. saponiCalc
- **URL:** https://saponicalc.com/calculator
- **Pricing:** Free (appears to be ad-supported)

#### Features
✅ **Modern web calculator**
✅ **Large oil database** (150+ oils including exotics like Abyssinian, Acai, Andiroba, Baobab, etc.)
✅ **Bar soap (NaOH), Liquid soap (KOH), and Hybrid/Dual Lye support**
✅ **Multiple water calculation methods** (lye concentration, water:lye ratio, % of oils)
✅ **Fragrance calculator** (multiple units: oz/lb, g/kg, % of oils)
✅ **Percentage or weight-based recipe building**
✅ **Clean, modern UI**

❌ **No visible additive support** in the interface
❌ **No cost calculator**
❌ **No recipe saving** (appears to be session-only)
❌ **No community features**

#### Assessment
**Solid single-purpose calculator.** Excellent oil database and clean interface, but lacks business features and additive support. Good for basic recipe formulation but not comprehensive enough for professional use.

---

## Feature Comparison Matrix

| Feature | Soapee | Sporiff | msbeaule | SMF | Soap Metrics | saponiCalc | MGA Need |
|---------|--------|---------|----------|-----|--------------|------------|----------|
| **Core Calculations** ||||||||
| SAP Calculation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| NaOH Support | ✅ | ? | ✅ | ✅ | ✅ | ✅ | ✅ |
| KOH Support | ✅ | ? | ❌ | ✅ | ✅ | ✅ | ❌ |
| Superfat % | ✅ | ? | ✅ | ✅ | ✅ | ✅ | ✅ |
| Fragrance Calc | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Quality Metrics** ||||||||
| Hardness | ✅ | ❌ | ❌ | ✅ | ✅ | ? | ✅ |
| Cleansing | ✅ | ❌ | ❌ | ✅ | ✅ | ? | ✅ |
| Conditioning | ✅ | ❌ | ❌ | ✅ | ✅ | ? | ✅ |
| Bubbly | ✅ | ❌ | ❌ | ✅ | ✅ | ? | ✅ |
| Creamy | ✅ | ❌ | ❌ | ✅ | ✅ | ? | ✅ |
| Longevity | ❌ | ❌ | ❌ | ? | ✅ | ? | ❌ |
| Stability | ❌ | ❌ | ❌ | ? | ✅ | ? | ❌ |
| Iodine Value | ✅ | ❌ | ❌ | ✅ | ✅ | ? | ✅ |
| INS Value | ✅ | ❌ | ❌ | ✅ | ✅ | ? | ✅ |
| Fatty Acid Profile | ✅ | ❌ | ❌ | ✅ | ✅ | ? | ✅ |
| **Additives** ||||||||
| Non-fat Additives | ❌ | ❌ | ❌ | 📝 | 📝 | ❌ | ✅ |
| Additive Quality Impact | ❌ | ❌ | ❌ | ❓ | ❓ | ❌ | **✅ REQUIRED** |
| **Business Features** ||||||||
| Recipe Storage | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| Cost Calculator | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| Inventory Mgmt | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Batch Management | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Output** ||||||||
| INCI Names | ✅ | ❌ | ❌ | ? | ? | ? | ✅ |
| PDF Export | ❌ | ❌ | ❌ | ? | ✅ | ? | ❌ |
| Recipe Instructions | ❌ | ❌ | ❌ | ? | ✅ | ? | ❌ |

**Legend:**
✅ = Confirmed present
❌ = Confirmed absent
? = Unknown/not visible from interface
📝 = Present but likely notes-only (no calculation impact)
❓ = Present but calculation impact unclear

---

## Critical Gap Analysis

### The Additive Problem

**What we want:** Custom non-fat additives (clays, salts, botanicals, etc.) that **affect soap bar quality metrics**.

**What exists:**
- **Open source:** ZERO projects support additives at all
- **Commercial platforms:** Two platforms (SMF, Soap Metrics) mention "additives" but it's unclear if they:
  - A) Just track additives for recipe notes/cost (most likely)
  - B) Actually incorporate additive effects into quality calculations (doubtful)

### Why This is Hard

Current quality metrics are calculated as **weighted averages of oil properties:**

```
Hardness = Sum(oil_percentage[i] * oil_hardness[i])
Cleansing = Sum(oil_percentage[i] * oil_cleansing[i])
etc.
```

This works because:
1. Each oil has known SAP value and quality contributions
2. These are well-documented in soap-making literature
3. The math is straightforward (linear combinations)

**Additives are different:**
1. They don't saponify (no SAP value for non-fats)
2. Effects may be non-linear (e.g., 2% clay ≠ double the effect of 1% clay)
3. Effects may be category-specific (kaolin clay vs bentonite vs activated charcoal)
4. Effects may interact with oil blend (salt in high-oleic vs high-lauric soap)
5. **Empirical data is sparse** - no standardized "clays.json" database exists

### What Would Be Required

To build additive quality impact:

1. **Research Phase:**
   - Literature review of additive effects on soap properties
   - Possibly empirical testing (make soap, measure results)
   - Consultation with experienced soap makers
   - Document typical usage ranges (e.g., clays: 1-3% of oils)

2. **Data Structure:**
   ```json
   {
     "name": "Kaolin Clay",
     "category": "clay",
     "typical_usage": {"min": 0.01, "max": 0.03, "unit": "percentage_of_oils"},
     "effects": {
       "hardness": "+5 at 2%",
       "creamy": "+3 at 2%",
       "cleansing": "no change",
       "note": "Linear up to 3%, diminishing returns above"
     }
   }
   ```

3. **Calculation Logic:**
   - Base calculations from oils (existing logic)
   - Apply additive modifiers (additive-specific logic)
   - Handle edge cases (multiple additives, interactions)

4. **Validation:**
   - Compare calculated values to real-world soap properties
   - Iterate on additive effect values based on feedback

---

## Technical Architecture Recommendations

Based on the analysis, here are recommendations for the MGA soap calculator:

### Option 1: Fork Soapee (Comprehensive)
**Pros:**
- Complete, professional codebase
- Proven architecture (API + React + PostgreSQL)
- User accounts, recipe database already built
- Quality metrics and INCI names already implemented
- Can focus development on additive feature addition

**Cons:**
- Substantial codebase to understand (~98% JavaScript)
- Requires PostgreSQL setup
- Author warns code is outdated (security concerns for public hosting)
- AGPLv3 license (requires derivative work to be open source)

**Effort:** 🔴 High (understanding existing code) + Medium (additive feature)
**Timeline:** 2-4 weeks to understand, 1-2 weeks to add additives
**Best for:** If you want a full-featured platform with community features

---

### Option 2: Build from Scratch (Clean Slate)
**Pros:**
- Modern tech stack (choose your preferred framework)
- No legacy code to understand
- Focused on exactly your requirements
- Can be simpler (no user accounts, database if not needed)
- Any license you want

**Cons:**
- Must implement all calculations from scratch
- Must build oil database
- Must build quality metrics logic
- No reference code for edge cases

**Effort:** 🔴 High (all features) + Medium (additive feature)
**Timeline:** 3-4 weeks for complete calculator + additives
**Best for:** If you want long-term maintainability and specific tech stack

---

### Option 3: Enhance Simple Calculator (Quick Start)
**Pros:**
- Start with msbeaule's simple code as reference
- Focus immediately on the unique additive feature
- Can build web-based or desktop
- Minimal dependencies

**Cons:**
- Must add all quality metrics (not in simple calculator)
- Must expand oil database significantly
- No UI framework (raw HTML/CSS/JS)

**Effort:** 🟡 Medium (quality metrics) + Medium (additives)
**Timeline:** 2-3 weeks total
**Best for:** If you want rapid iteration and learning experience

---

### Option 4: API-First Hybrid Approach (Recommended)
**Pros:**
- Build calculation engine as standalone library/API
- Can reuse Soapee's calculation logic as reference
- Decouple UI from calculations
- Start with simple web UI, upgrade later
- Can add desktop app, mobile app later using same engine

**Cons:**
- Requires good API design upfront
- Slightly more complex initial architecture

**Effort:** 🟡 Medium (API design) + Medium (UI) + Medium (additives)
**Timeline:** 2-3 weeks total
**Best for:** If you want flexibility and future expansion

**Recommended Stack:**
- **Backend:** Python (soap makers understand it, good for calculations) or Node.js (consistent with Soapee)
- **API:** FastAPI (Python) or Express (Node.js)
- **Frontend:** React (modern, proven in Soapee) or Svelte (simpler, faster learning)
- **Database:** SQLite (simple) or PostgreSQL (if scaling later)
- **Calculation Engine:** Standalone module that can be tested independently

---

## Calculation Logic Reference

From the Go prototype (`soapcalc/proto/main.go`), here's how quality is calculated:

```go
// For each oil in recipe:
recipe.Hardness += oilPercentage * oil.Hardness
recipe.Cleansing += oilPercentage * oil.Cleansing
recipe.Condition += oilPercentage * oil.Condition
recipe.Bubbly += oilPercentage * oil.Bubbly
recipe.Creamy += oilPercentage * oil.Creamy

// Fatty acids:
recipe.Lauric += oilPercentage * oil.Lauric * 100
recipe.Myristic += oilPercentage * oil.Myristic * 100
recipe.Palmitic += oilPercentage * oil.Palmitic * 100
// etc...

// Lye calculation:
recipe.LyeWeight += oil.NaOH * oilWeight
recipe.LyeWeight *= (1 - superFatPercentage)

// Water:
recipe.WaterWeight = waterToLipidRatio * totalOilWeight
```

**For additives, we'd extend this to:**

```python
# After base calculations
for additive in recipe.additives:
    if additive.category == "clay":
        recipe.hardness += calculate_clay_hardness_boost(additive.amount, additive.type)
        recipe.creamy += calculate_clay_creamy_boost(additive.amount, additive.type)
    elif additive.category == "salt":
        recipe.hardness += calculate_salt_hardness_boost(additive.amount)
        # Salt may reduce lather
        recipe.bubbly -= calculate_salt_bubbly_reduction(additive.amount)
    # etc.
```

---

## Next Steps

### Immediate (Research Phase)
1. **Interview Shale** about:
   - Which additives you actually use (clays? salts? botanicals?)
   - How much you typically use
   - What effects you've observed (harder bar? better lather? different feel?)
   - Priorities: Which quality metrics matter most to MGA soap?

2. **Literature Review:**
   - Search soap-making books for additive effects
   - Check soap-making forums for empirical data
   - Look for any academic papers on soap formulation

3. **Feature Prioritization:**
   - Do you need INCI names? (You said you like this feature)
   - Do you need recipe storage or just calculation?
   - Do you need cost analysis?
   - Desktop app or web app?

### Implementation Phase (After Research)
1. **Choose architecture** (Option 1-4 above)
2. **Build MVP** with oil calculations only (validate core logic)
3. **Add additives database** based on research findings
4. **Implement additive calculations** with test cases
5. **User testing** with actual soap batches
6. **Iterate** on additive effect values based on real results

---

## Conclusion

**The bad news:** No existing solution (open source or commercial) solves your core requirement. Building additive quality impact is genuinely novel functionality.

**The good news:**
1. The basic calculation engine is well-understood (Soapee and others prove it works)
2. You have a clear feature differentiator (nobody else does this)
3. The core challenge is data (researching additive effects), not code complexity
4. You can start with a simple MVP and iterate

**Recommended Path:**
1. Start with Soapee's calculation logic as reference (don't fork entire app)
2. Build new, focused calculator with modern stack
3. Implement additives as first-class feature from day one
4. Test extensively with real soap batches
5. Possibly release as open source to help other soap makers (after validating it works)

This could be a genuinely useful contribution to the soap-making community - IF the additive calculations are accurate.
