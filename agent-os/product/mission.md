# Product Mission

## Vision

MGA Soap Calculator is the in-house formulation and labeling tool for Midnight Garden Apothecary — Shale and Jackie Greysson's cottage-industry handmade soap and skincare brand, sold through Raven's Eye Consulting. It replaces the tab-juggling workflow of a 20-year-old web calculator plus a separate INCI generator plus a spreadsheet of additive notes with one owner-operated service that does the saponification math, models how additives actually change soap quality, and emits print-ready ingredient labels. Success looks like Shale and Jackie reaching for it on every batch, trusting its numbers, and spending their hands-on time on soap instead of on arithmetic and label formatting.

## Users

**Primary — Shale and Jackie (the owners).** Cottage-industry handmade soap and skincare under the MGA brand. Small batches, retail sales through REC's storefront, compliance labels on every product. They use the calculator to plan recipes, validate quality metrics, and generate the INCI ingredient declarations that go on each bar.

**Near-term secondary — trusted peers in the MGA/REC network.** Invited accounts only. Other small soap makers Shale and Jackie already know and want to share recipes or formulation notes with. No public signup. Same tool, scoped to their own user.

**Longer-term (aspirational, not committed) — indie soap makers broadly.** A hypothetical public tier. Not built, not planned in detail, explicitly gated behind proof of sustained demand from the owners and their peers first. See Non-goals.

## Problems

- **Existing free calculators** (SoapCalc, Bramble Berry's Lye Calc, The Sage) are dated web apps with no additive effect modeling, no INCI output, no per-user persistence, and UX stuck in 2005.
- **Commercial alternatives** (Soapmaker 3) are Windows-only desktop apps around $80 with outdated interfaces and no API to script against.
- **Additive effect modeling is absent industry-wide.** Every other tool treats oat flour, honey, goat milk, sodium lactate, clays, etc. as opaque — yet the literature on how each shifts hardness, lather, and conditioning exists. Shale and Jackie were doing this lookup by hand against a private notes file.
- **INCI label generation lives in a separate tool.** Retail compliance requires an ingredient declaration per product; flipping between calculator and labeler costs time and invites transcription errors.
- **No persistence tied to an owner.** Free calculators let you download a PDF and walk away. There's no "show me the last three goat milk recipes I ran" without a separate spreadsheet.

## Differentiators

- **Additive effect modeling grounded in cited research.** The unique capability. Each additive has a documented set of quality-metric modifiers, scaled by usage rate. No other calculator does this.
- **INCI label generation in the same tool.** Three formats (raw oils, saponified names, common names) emitted directly from the same recipe. The compliance artifact is a side effect of the calculation, not a separate task.
- **API-first, owner-operated.** A headless FastAPI service means a future desktop app, CLI, or mobile client can share one source of truth. Self-hosted on the Greysson OpenShift SNO keeps operating costs, data stewardship, and pace of change with the owners — not a vendor.

## Non-goals

- **Not a SaaS chasing growth.** MGA is a cottage industry. The product scales if the business does, not the other way around.
- **Not a marketplace.** No buying ingredients, no matching suppliers, no transactional commerce inside the tool.
- **Not a community platform.** No public recipe feeds, no social features, no comments, no ratings.
- **Not a generic e-commerce app.** REC's Shopify is the storefront. This tool integrates with it at most; it does not replace it.
- **Not a knowledge base or tutorial site.** Docs for users, yes. Guides on how to make soap, no — that's not the scope.

## Success metrics

- **Owner usage**: Shale and Jackie run every production batch through the calculator for at least one full quarter, tracked by persisted calculations tied to their accounts.
- **Recipe-to-label time**: Less than 10 minutes from "I want to try this recipe" to a printable INCI declaration for the finished bar.
- **Additive-modeling accuracy**: When the owners compare predicted quality metrics against batch outcomes, predictions track reality closely enough that they keep using the feature (qualitative — owner judgment is the benchmark).
- **Self-sufficiency**: The owners can use the tool end to end without Grimm in the loop for day-to-day recipe work.
