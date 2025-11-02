# Product Mission

## Pitch
MGA Soap Calculator is an API-first soap formulation platform that helps professional and small business soap makers optimize recipes by providing the industry's first comprehensive modeling of how non-fat additives (clays, salts, botanicals) affect soap quality metrics.

## Users

### Primary Customers
- **MGA Automotive (Shale's soap business)**: Internal production use for professional soap formulation and cost management
- **Professional Soap Makers**: Small to medium soap businesses requiring precise formulation control
- **Artisan Soap Crafters**: Serious hobbyists and micro-businesses seeking data-driven recipe development

### User Personas

**Professional Soap Maker** (30-55)
- **Role:** Small business owner, production manager, or formulation specialist
- **Context:** Creating consistent, high-quality soap products for retail or wholesale
- **Pain Points:**
  - Existing calculators don't account for additive effects on soap properties
  - Manual cost calculations are time-consuming and error-prone
  - No way to predict how clays, salts, or botanicals impact final soap quality
  - Difficulty maintaining consistent formulations across batches
- **Goals:**
  - Optimize recipes for specific quality profiles (hardness, cleansing, conditioning)
  - Accurate cost analysis for pricing decisions
  - Reliable predictions of how additives affect final product
  - Efficient batch management and scaling

## The Problem

### No Calculator Handles Additive Quality Impact

Existing soap calculators (both open source like SoapCalc and commercial solutions) focus exclusively on saponification calculations and base oil properties. **None model how non-fat additives affect the final soap's quality metrics.**

This creates a critical gap: professional soap makers using clays (kaolin, bentonite), salts (sea salt, Himalayan pink), botanicals (oatmeal, coffee grounds), or other additives must rely on guesswork or extensive trial-and-error to understand how these ingredients impact hardness, cleansing power, conditioning, lather quality, and other key properties.

**Our Solution:** Build the industry's first calculator that models additive effects on soap quality through research-backed data, enabling data-driven formulation decisions for professional soap makers.

## Differentiators

### First-to-Market Additive Quality Modeling
Unlike every existing calculator (SoapCalc, Mendrulandia, The Sage, Soapmaker's Friend, etc.), we provide quantitative modeling of how non-fat additives affect soap properties.

This results in:
- **Competitive Advantage:** Unique capability no competitor offers
- **User Value:** Reduced R&D costs through better first-iteration formulations
- **Market Position:** Premium tool for serious soap makers, not hobbyist-focused basic calculators

### API-First Architecture
Starting with REST API enables:
- **Immediate Internal Use:** MGA Automotive can integrate into production workflows immediately
- **Future Flexibility:** Web interface, mobile apps, or third-party integrations built on stable foundation
- **Professional Focus:** Targets business users who value automation and integration

### Research-Driven Approach
Phase 1 includes dedicated additive research to ensure quality impact calculations are evidence-based, not guesswork. This scientific foundation differentiates us from competitors who simply aggregate anecdotal information.

## Key Features

### Core Calculation Engine
- **Saponification Calculations:** Lye requirements, superfat percentages, water ratios
- **Quality Metrics:** Hardness, Cleansing, Conditioning, Bubbly Lather, Creamy Lather scores
- **Fatty Acid Profiles:** Complete breakdown of lauric, myristic, palmitic, stearic, oleic, linoleic, linolenic acids
- **Additive Impact Modeling:** Quantitative effects of clays, salts, botanicals on quality metrics (unique feature)

### Recipe Management
- **Recipe Storage:** PostgreSQL-backed persistent storage with version history
- **Cost Calculator:** Per-batch and per-unit cost analysis with ingredient pricing
- **Batch Scaling:** Automatic recalculation for different production volumes
- **Recipe Organization:** Categorization, tagging, search capabilities

### Professional Features
- **INCI Name Generation:** Automatic cosmetic ingredient labeling compliance
- **Fragrance Calculator:** Essential oil and fragrance blending ratios
- **Export/Import:** Recipe sharing and backup in standard formats
- **API Access:** RESTful endpoints for integration into production systems

### Future Features (Post-MVP)
- **Web Interface:** Public-facing recipe builder for external customers
- **Community Features:** Recipe sharing, rating, commenting (if desired)
- **Mobile Access:** Responsive web or native mobile apps
- **Advanced Analytics:** Historical cost trends, supplier comparison, batch tracking

## Success Metrics

### Phase 1: Internal API Success
- **Adoption:** MGA Automotive using API for all new recipe development
- **Accuracy:** Calculation results match manual verification within 1% tolerance
- **Research Quality:** Additive data sourced from peer-reviewed sources or validated testing
- **Performance:** API response times <200ms for standard calculations
- **Reliability:** 99.9% uptime for internal use

### Phase 2: Enhanced API Maturity
- **Feature Completeness:** INCI generation, fragrance calculator, batch management operational
- **Documentation:** Comprehensive API docs with examples for all endpoints
- **Testing:** >90% code coverage with unit and integration tests
- **Versioning:** Stable API contract with backward compatibility guarantees

### Phase 3: Public Web Launch
- **User Acquisition:** External soap makers adopting the platform
- **User Satisfaction:** Positive feedback on unique additive modeling capability
- **Revenue (if applicable):** Subscription or usage-based revenue stream established
- **Market Recognition:** Industry awareness of unique additive modeling capability

## Strategic Goals

### Immediate (Phase 1)
1. **Complete Additive Research:** Establish data foundation for quality impact modeling
2. **Build MVP API:** Core calculations, recipe storage, cost analysis operational
3. **Internal Deployment:** MGA Automotive using system in production

### Short-Term (Phase 2)
1. **Feature Parity:** Match analysis requirements (INCI, fragrance, batch management)
2. **API Stability:** Production-grade reliability, documentation, versioning
3. **Validation:** Real-world testing confirms additive modeling accuracy

### Long-Term (Phase 3+)
1. **Public Web Interface:** External user access through modern web application
2. **Market Expansion:** Professional soap maker community adoption
3. **Platform Evolution:** Mobile apps, community features, advanced analytics
4. **Revenue Generation:** Sustainable business model (if desired)

## Product Philosophy

**Data-Driven Formulation:** Move soap making from art to science through quantitative modeling and research-backed calculations.

**API-First Design:** Start with programmatic access to enable automation, integration, and future flexibility.

**Professional Focus:** Target serious soap makers who value precision, consistency, and business efficiency over casual hobbyists.

**Unique Value Creation:** Solve problems competitors ignore (additive quality impact) rather than competing on existing features.

**Research Foundation:** Build credibility through evidence-based additive data, not anecdotal community wisdom.
