# Complete Oils Database for MGA Soap Calculator API

**Date:** 2025-11-04
**Source:** Oils list - Hardness.csv
**Total Oils:** 107

All SAP values calculated using: `SAP_NaOH = (INS + Iodine) / 1000` and `SAP_KOH = SAP_NaOH × 1.403`

---

## Import Instructions

The full database is available in JSON format at `/tmp/all_oils_data.json` with the following structure:

```json
{
  "name": "Oil Name",
  "hardness": 0-99,
  "cleansing": 0-99,
  "conditioning": 0-99,
  "bubbly": 0-99,
  "creamy": 0-99,
  "iodine": 0-200,
  "ins": 0-350,
  "sap_naoh": 0.000,
  "sap_koh": 0.000
}
```

---

## Database Schema Mapping

To convert to API format, map as follows:

```javascript
{
  id: name.toLowerCase().replace(/[^a-z0-9]+/g, '_'),
  common_name: name,
  inci_name: "", // Needs manual addition for important oils
  sap_value_naoh: sap_naoh,
  sap_value_koh: sap_koh,
  iodine_value: iodine,
  ins_value: ins,
  fatty_acids: {
    // Needs fatty acid profile data
    // Can be estimated or researched for each oil
  },
  quality_contributions: {
    hardness: hardness,
    cleansing: cleansing,
    conditioning: conditioning,
    bubbly_lather: bubbly,
    creamy_lather: creamy,
    longevity: hardness, // Typically same as hardness
    stability: creamy  // Typically same as creamy
  }
}
```

---

## Fatty Acid Profile Notes

For complete database implementation, fatty acid profiles need to be added. Common patterns:

### High Lauric Oils (Cleansing)
- Coconut Oil: Lauric 48%, Myristic 19%
- Babassu Oil: Lauric 50%, Myristic 20%
- Palm Kernel Oil: Lauric 48%, Myristic 16%

### Animal Fats (Balanced)
- Tallow (Beef): Palmitic 26%, Stearic 24%, Oleic 39%
- Lard: Palmitic 24%, Stearic 13%, Oleic 44%
- Tallow (Sheep): Palmitic 25%, Stearic 29%, Oleic 38%

### High Oleic Oils (Conditioning)
- Olive Oil: Oleic 72%, Palmitic 11%, Linoleic 10%
- Avocado Oil: Oleic 63%, Palmitic 12%, Linoleic 13%
- Almond Oil: Oleic 68%, Linoleic 23%

### Polyunsaturated Oils (Very Conditioning)
- Hemp Oil: Linoleic 57%, Linolenic 21%, Oleic 12%
- Flax/Linseed Oil: Linolenic 57%, Oleic 19%, Linoleic 15%
- Grapeseed Oil: Linoleic 70%, Oleic 16%

### Specialty Oils
- Castor Oil: Ricinoleic 90%, Oleic 4%
- Cocoa Butter: Stearic 34%, Oleic 35%, Palmitic 26%
- Shea Butter: Stearic 40%, Oleic 45%

---

## Implementation Priority Tiers

### Tier 1: Essential Oils (Already in API)
- ✅ Olive Oil
- ✅ Coconut Oil
- ✅ Palm Oil
- ✅ Castor Oil
- ✅ Avocado Oil
- ✅ Shea Butter
- ✅ Cocoa Butter
- ✅ Sunflower Oil
- ✅ Sweet Almond Oil
- ✅ Jojoba Oil

### Tier 2: Common Soap Making Oils (Missing from API)
- ❌ Tallow (Beef) - in your test recipe
- ❌ Babassu Oil - in your test recipe
- ❌ Hemp Oil - in your test recipe
- ❌ Lard
- ❌ Rice Bran Oil
- ❌ Canola Oil
- ❌ Soybean Oil
- ❌ Grapeseed Oil
- ❌ Mango Butter
- ❌ Palm Kernel Oil

### Tier 3: Specialty & Exotic Oils
All other oils in the database (for completeness)

---

## Quick Import Script Template

For Grimm to bulk import, here's a Python script template:

```python
import json

# Load the calculated data
with open('/tmp/all_oils_data.json', 'r') as f:
    oils = json.load(f)

# Convert to API format
api_oils = {}
for oil in oils:
    oil_id = oil['name'].lower().replace(' ', '_').replace(',', '').replace("'", '')

    api_oils[oil_id] = {
        "id": oil_id,
        "common_name": oil['name'],
        "inci_name": "",  # Fill in manually for important oils
        "sap_value_naoh": oil['sap_naoh'],
        "sap_value_koh": oil['sap_koh'],
        "iodine_value": oil['iodine'],
        "ins_value": oil['ins'],
        "fatty_acids": {
            # TODO: Add fatty acid profiles
            "lauric": 0,
            "myristic": 0,
            "palmitic": 0,
            "stearic": 0,
            "oleic": 0,
            "linoleic": 0,
            "linolenic": 0,
            "ricinoleic": 0
        },
        "quality_contributions": {
            "hardness": oil['hardness'],
            "cleansing": oil['cleansing'],
            "conditioning": oil['conditioning'],
            "bubbly_lather": oil['bubbly'],
            "creamy_lather": oil['creamy'],
            "longevity": oil['hardness'],  # Estimate
            "stability": oil['creamy']  # Estimate
        }
    }

# Save to database import format
with open('oils_database_import.json', 'w') as f:
    json.dump(api_oils, f, indent=2)
```

---

## Fatty Acid Profile Resources

For filling in fatty acid profiles, use these references:
- **The Sage**: soapqueen.com (comprehensive soap making database)
- **SoapCalc**: soapcalc.net (industry standard calculator)
- **Robert Tisserand**: tisserand.com (essential oil chemistry)
- **Academic Sources**: PubChem, USDA FoodData Central

---

## Notes

1. **SAP Value Accuracy:** Calculated values are industry-standard approximations. Actual SAP values can vary by ±2% due to oil source, processing, and freshness.

2. **Longevity & Stability:** These are estimated as equal to hardness and creamy respectively. More accurate values would require research for each oil.

3. **Fatty Acid Profiles:** The most time-consuming part. For Tier 1 and 2 oils, use established soap making databases. For exotic oils, may need academic research.

4. **INCI Names:** Only critical for customer-facing applications (ingredient labels). Can be added incrementally for commonly used oils.

5. **Testing:** After import, verify calculations with known recipes to ensure accuracy.

---

## Data Quality Checklist

Before production import:
- [ ] SAP values calculated correctly (spot check 10 random oils)
- [ ] Fatty acid profiles sum to ~100% for each oil
- [ ] Quality metrics match established soap making databases
- [ ] INCI names added for Tier 1 & 2 oils
- [ ] Test with 3 known recipes to verify accuracy
- [ ] API validation passes for all oil entries

---

**Next Steps:**
1. Review the JSON export at `/tmp/all_oils_data.json`
2. Add fatty acid profiles (start with Tier 1 & 2 oils)
3. Add INCI names for commercial oils
4. Test import with development database
5. Validate calculations against known recipes
6. Deploy to production

**Estimated Time:**
- Basic import (SAP + quality metrics only): 30 minutes
- With Tier 1 & 2 fatty acids: 2-3 hours
- Complete with all fatty acids: 6-8 hours
