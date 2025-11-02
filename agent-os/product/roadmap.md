# Product Roadmap

## Phase 1: Research & API Foundation (MVP)

**Goal:** Establish research foundation and build working API for MGA Automotive internal use

1. [ ] **Additive Research & Data Collection** — Research how non-fat additives (clays, salts, botanicals) affect soap quality metrics. Collect data from peer-reviewed sources, industry publications, and validated testing. Create structured database schema for additive properties and quality impact coefficients. `L`

2. [ ] **Core Calculation Engine** — Implement saponification calculations (lye requirements, superfat, water ratios), quality metrics (Hardness, Cleansing, Conditioning, Bubbly, Creamy), and fatty acid profile analysis. Build mathematical models for base soap properties before additive effects. `M`

3. [ ] **Additive Impact Modeling** — Develop algorithms that apply research-backed coefficients to model how additives modify base soap quality metrics. Integrate with core calculation engine to provide complete formulation analysis including non-fat ingredients. `L`

4. [ ] **Recipe Storage System** — Design and implement PostgreSQL database schema for recipes, ingredients, additives, and batch history. Create CRUD operations for recipe management with version control and timestamp tracking. `M`

5. [ ] **Cost Calculator** — Build cost analysis engine that calculates per-batch and per-unit costs based on ingredient pricing, batch size, and waste factors. Support bulk pricing tiers and supplier comparison. `S`

6. [ ] **REST API Foundation** — Develop FastAPI application with endpoint routing, request validation, error handling, and response formatting. Implement core endpoints: calculate saponification, analyze quality metrics, CRUD recipes, calculate costs. `M`

7. [ ] **API Authentication** — Implement JWT-based authentication for internal API access. Support API key generation for service-to-service integration. Role-based access control for future multi-user scenarios. `S`

8. [ ] **API Documentation** — Generate interactive API documentation using FastAPI's automatic OpenAPI/Swagger integration. Include endpoint descriptions, request/response examples, and authentication instructions. `XS`

9. [ ] **Internal Deployment** — Deploy API to internal infrastructure using Docker containers. Set up PostgreSQL database with migrations. Configure monitoring and logging for production use by MGA Automotive. `M`

**Success Criteria:** MGA Automotive using API for soap recipe development, calculations accurate within 1% tolerance, additive research complete with documented sources

---

## Phase 2: Enhanced API Features

**Goal:** Achieve feature parity with analysis requirements, production-grade API stability

10. [ ] **INCI Name Generation** — Implement automatic cosmetic ingredient nomenclature generation following international standards. Support multi-language INCI names, synonym handling, and proper alphabetical ordering for labels. `M`

11. [ ] **Fragrance Calculator** — Build fragrance blending calculator for essential oils and fragrance oils. Calculate safe usage rates, blend ratios, and scent strength estimates. Support fragrance oil supplier databases. `S`

12. [ ] **Advanced Batch Management** — Extend recipe system with batch production tracking, scaling calculations, yield predictions, and actual vs. expected comparisons. Track batch notes, environmental conditions, and quality observations. `M`

13. [ ] **Recipe Export/Import** — Implement export to standard formats (JSON, CSV, PDF recipe cards). Support import from common soap calculator formats for migration. Backup and restore capabilities. `S`

14. [ ] **API Versioning** — Introduce API versioning strategy (/v1/, /v2/ routes) to maintain backward compatibility. Deprecation warnings for old endpoints. Comprehensive migration guides. `S`

15. [ ] **Performance Optimization** — Profile and optimize calculation algorithms, database queries, and API response times. Implement caching for frequently-accessed data. Target <200ms response times for standard calculations. `M`

16. [ ] **Comprehensive Testing** — Achieve >90% code coverage with pytest unit tests. Implement API integration tests with httpx. Add property-based testing for calculation accuracy. Automated test suite in CI/CD pipeline. `M`

17. [ ] **Production Monitoring** — Set up application performance monitoring (APM), error tracking, and usage analytics. Create dashboards for API health, calculation accuracy validation, and usage patterns. `S`

**Success Criteria:** Complete feature set operational, API stable with versioning, >90% test coverage, production monitoring active

---

## Phase 3: Public Web Interface

**Goal:** Launch public-facing web application for external soap makers

18. [ ] **User Authentication & Accounts** — Build user registration, login, password reset, and email verification. Support OAuth for social login (Google, GitHub). User profile management and preferences. `M`

19. [ ] **React Frontend Foundation** — Initialize React 18 + TypeScript + Tailwind CSS application with Vite build tooling. Set up component library, routing (React Router), and state management. Connect to backend API. `M`

20. [ ] **Recipe Builder UI** — Create interactive recipe formulation interface with ingredient selection, quantity inputs, additive selection, and real-time calculation updates. Display quality metrics with visual indicators and explanations. `L`

21. [ ] **Recipe Management Dashboard** — Build user dashboard for viewing, organizing, searching, and filtering saved recipes. Support recipe collections, favorites, and tags. Recipe sharing controls (private/public/shared-link). `M`

22. [ ] **Cost Analysis Interface** — Design cost breakdown visualization showing per-ingredient costs, batch totals, and per-unit pricing. Support ingredient price entry and supplier comparison tools. `S`

23. [ ] **INCI & Labeling Tools** — Create label generation interface that outputs properly formatted INCI ingredient lists, allergen warnings, and regulatory compliance information. Printable/PDF export for product labels. `M`

24. [ ] **Responsive Design** — Ensure mobile-first responsive design works across desktop, tablet, and mobile devices. Touch-friendly interfaces for recipe entry on tablets. Progressive Web App (PWA) capabilities. `M`

25. [ ] **Public Documentation** — Write user guides, tutorial videos, FAQ, and getting-started documentation for external users. Explain quality metrics, additive effects, and how to interpret calculation results. `S`

26. [ ] **Production Web Deployment** — Deploy frontend and backend to production hosting (AWS, DigitalOcean, or similar). Set up CDN for static assets, SSL certificates, and domain configuration. Implement CI/CD pipeline for automated deployments. `M`

**Success Criteria:** Public web app live and accessible, external users successfully creating and managing recipes, positive user feedback on additive modeling capability

---

## Future Considerations (Beyond Phase 3)

### Mobile Applications
- Native iOS/Android apps or React Native cross-platform application
- Offline calculation support with local database sync
- Camera-based ingredient barcode scanning for quick entry
- Push notifications for batch reminders or recipe sharing

### Community Features
- Public recipe sharing marketplace
- User ratings, reviews, and comments on recipes
- Soap maker profiles and following system
- Community forums or discussion boards
- Recipe remix/fork functionality (build on others' recipes)

### Advanced Analytics
- Historical cost trend analysis and alerts for price increases
- Supplier recommendation engine based on cost and availability
- Batch quality tracking with statistical process control
- Predictive modeling for shelf life and stability

### Business Features
- Multi-user team accounts for soap businesses
- Batch production scheduling and workflow management
- Inventory tracking integration
- Customer order management and recipe assignment
- Invoicing and cost accounting integration

### Supply Chain Integration
- Direct ingredient ordering from supplier APIs
- Real-time pricing and availability updates
- Automated reorder suggestions based on batch schedules
- Supplier rating and reliability tracking

### Scientific Expansion
- pH prediction modeling for finished soap
- Shelf life and stability predictions
- Cure time optimization recommendations
- Water activity calculations for preservation

---

> Notes
> - Roadmap ordered by technical dependencies and product architecture
> - Phase 1 focuses on research foundation and API for immediate internal value
> - Phase 2 enhances API to production-grade with full feature set
> - Phase 3 adds public web interface for external market expansion
> - Future considerations are conceptual and not committed deliverables
> - Each item represents an end-to-end functional and testable feature
> - Additive research (item 1) is critical path for unique value proposition
