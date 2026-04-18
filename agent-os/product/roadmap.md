# Product Roadmap

## Done (as of 2026.4.18)

Current running version: **2026.4.18** on OpenShift SNO at `https://mga-soap-calculator.apps.sno.greysson.com`.

- Full calculation engine: NaOH / KOH / mixed lye saponification with purity adjustment
- Three water-calculation methods: % of oils, lye concentration, water:lye ratio
- 7 quality metrics: hardness, cleansing, conditioning, bubbly, creamy, longevity, stability
- Fatty acid profile + sat:unsat ratio
- Smart additive calculator with research-backed effect modeling (the differentiator)
- Ingredient database: 137 entries (60+ oils, 30+ additives, essential oils, colorants)
- INCI label generation in three formats: raw oils, saponified names, common names
- User auth: Argon2id password hashing + JWT (24h expiry)
- Calculation persistence and retrieval, per-user, ownership-validated
- 454 passing tests, 79% coverage, CI green
- Refactor campaign complete: Phase 0 (ruff + CI), Phase 1 (mechanical), Phase 2 (structural), Phase 3 (pipeline split of the big handler)
- OpenShift SNO deployment: Namespace, Secret, Postgres StatefulSet, Deployment, Service, edge-TLS Route, on-cluster BuildConfig
- Ansible role `mga_soap_calculator_ocp` in `greysson-homelab` manages everything above
- CalVer versioning adopted today (2026.4.18)

---

## Phase A — Make it usable by the owners

**Why this phase.** The API works. The owners don't. Shale and Jackie are non-technical; Swagger docs and curl commands are not a production workflow. This phase builds the interface that lets them actually reach for the tool on every batch — which is the entire point of success metric #1 in `mission.md`.

- [ ] **Frontend UI — recipe builder** — Web UI for entering oils, water method, additives, superfat; shows live quality metrics, fatty acid profile, and INCI preview as the recipe changes. `L`
- [ ] **Mobile-friendly layout** — Responsive design that works on a phone or tablet in the garage/kitchen, not just a laptop. `M`
- [ ] **Save / load / list recipes** — Authenticated UI over the existing persistence endpoints: dashboard of the owner's saved calculations, rename, delete, duplicate. `S`
- [ ] **Batch scaling** — Take a saved recipe, enter target bar count or total oil weight, regenerate weights and labels scaled proportionally. `S`
- [ ] **Recipe sharing by URL** — Generate a link that pre-fills the builder with a recipe's ingredients (read-only view for the recipient; they can save a copy if authenticated). `S`
- [ ] **PDF export** — Print-ready recipe sheet plus INCI labels for a batch. One PDF per batch, owner-branded. `M`
- [ ] **Dev-loop frontend tooling** — Pick frontend stack (TypeScript + Bun + a framework TBD in Phase A planning), wire it into the Ansible deployment and the existing OCP BuildConfig pipeline. `M`

---

## Phase B — Integrate with the business

**Why this phase.** Once Shale and Jackie use the calculator for every batch, the natural next pains are cost/pricing and inventory. This phase wires the tool into the money side of MGA and the REC storefront so a recipe isn't an island — it's connected to what's in the cabinet, what each bar costs, and how the retail label looks.

- [ ] **Ingredient cost tracking** — Store purchase price + unit weight per ingredient; report per-batch and per-bar cost; suggest retail markup. `M`
- [ ] **Shopify inventory integration** — Read REC's Shopify inventory for base ingredients; flag when a recipe calls for more than what's in stock. Read-only to start; no writes to Shopify. `L`
- [ ] **Photo attachments per recipe** — Upload trace, unmolded, cured photos against a recipe for future reference. Object storage via OCP persistent volume or S3-compatible backend (TBD). `M`
- [ ] **Peer invited accounts** — Invite-only signup: Shale or Jackie sends an invite, recipient creates an account, can save their own recipes and receive shared URLs. No public signup. `M`
- [ ] **Custom branding for labels** — MGA logo, product name, net weight, batch number on the PDF label output. `S`
- [ ] **Recipe tags and search** — Tag a recipe (goat milk, holiday, test) and filter the dashboard by tag. `S`

---

## Phase C — Prove demand before public launch

**Why this phase.** This is aspirational and explicitly gated. It only moves forward if Shale and Jackie decide there is sustained demand from their peer network that warrants opening the tool up, and if the operating cost of doing so stays compatible with the cottage-industry posture in `mission.md`. Do not start any of these without owner sign-off.

- [ ] **Public signup + rate limiting** — Open registration with email verification; per-user and per-IP rate limits on calculation and label endpoints. `M`
- [ ] **Stripe subscriptions** — Paid tier for public users (free tier stays for owners and invited peers). Webhook handling, entitlements, billing portal. `L`
- [ ] **Multi-tenancy hardening** — Audit every query for user-scope enforcement, add row-level security, per-tenant rate limits, separate usage telemetry. `L`
- [ ] **Admin dashboard** — Owner-facing view of users, subscriptions, usage, errors, and moderation tools. `M`
- [ ] **Observability stack** — Structured logging, error tracking (Sentry or similar), metrics beyond OCP defaults (Prometheus), dashboards (Grafana). `M`
- [ ] **Mobile app (iOS)** — Native or React Native client consuming the same API. Only if Phase A frontend proves demand on mobile web first. `L`
- [ ] **Desktop companion** — Electron or Tauri wrapping the frontend for offline-capable local use. Only if owners request it. `L`

---

## Notes

- Order reflects dependency and business value. Phase A blocks the mission: without a UI, non-technical owners cannot use the tool. Phase B only makes sense once Phase A exists. Phase C does not start without explicit owner approval.
- Sizes: **S** = 2-3 days, **M** = 1 week, **L** = 2+ weeks. Adjust as specs are written.
- Every item is end-to-end (backend + any needed frontend + any IaC changes in `greysson-homelab`) and independently testable.
- Roadmap is a living document. Reorder when reality demands it; document the reason in the commit message.
