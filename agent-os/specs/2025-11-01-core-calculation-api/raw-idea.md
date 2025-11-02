# Core Soap Calculation API

**Date:** 2025-11-01
**Status:** Shaping
**Priority:** High - Phase 1 MVP

## Feature Summary
REST API endpoint for comprehensive soap recipe calculations including unique additive effect modeling.

## Key Requirements (Initial)
- Accept recipe input (oils, lye type, water, additives)
- Calculate saponification values
- Calculate quality metrics from oil blend
- Apply additive effects to quality metrics (UNIQUE)
- Return comprehensive calculation results
- Support multiple lye types (NaOH, KOH)
- Include fatty acid profiles
- Return INS and Iodine values

## Target User
MGA Automotive (Shale's soap business) - internal API use

## Competitive Advantage
First calculator to model non-fat additive effects on soap quality metrics

## Context Files
- Product Mission: agent-os/product/mission.md
- Roadmap: agent-os/product/roadmap.md
- Tech Stack: agent-os/product/tech-stack.md
- Additive Research: agent-os/research/soap-additive-effects.md
