# Agent OS Integration for MGA Soap Calculator

## Project Context

**Project**: MGA Soap Calculator
**Purpose**: Soap formulation calculator with custom additive support
**Unique Feature**: Unlike existing calculators, this supports non-fat additives (clays, salts, botanicals) with quality impact calculations

**Tech Stack**: TBD (run workflow to define)

## Available Workflows

This project uses Agent OS for spec-driven development. Workflows are available in `agent-os/commands/`:

### Product Planning
- **Location**: `agent-os/commands/plan-product/`
- **Purpose**: Create mission, roadmap, tech-stack documents
- **Output**: Files in `agent-os/product/`

### Specification Development
- **Shape Spec**: `agent-os/commands/shape-spec/` - Initialize and outline feature spec
- **Write Spec**: `agent-os/commands/write-spec/` - Complete detailed specification
- **Output**: Files in `agent-os/specs/[feature-name]/`

### Implementation
- **Create Tasks**: `agent-os/commands/create-tasks/` - Break spec into atomic tasks
- **Implement Tasks**: `agent-os/commands/implement-tasks/` - Build feature with verification
- **Orchestrate Tasks**: `agent-os/commands/orchestrate-tasks/` - Advanced multi-agent implementation
- **Output**: Working code + verification reports

## Coding Standards

Follow standards in `agent-os/standards/`:

### Global Standards
- `global/coding-style.md` - Code formatting and style conventions
- `global/commenting.md` - Documentation and comment standards
- `global/conventions.md` - Project-wide naming and organization
- `global/error-handling.md` - Error handling patterns
- `global/truth-safety.md` - Truth-first development principles
- `global/validation.md` - Input validation and data integrity

### Backend Standards
- `backend/api.md` - API design and implementation
- `backend/models.md` - Data model patterns
- `backend/queries.md` - Database query standards
- `backend/migrations.md` - Schema migration practices

### Frontend Standards
- `frontend/components.md` - Component architecture
- `frontend/css.md` - Styling conventions
- `frontend/accessibility.md` - WCAG compliance
- `frontend/responsive.md` - Responsive design patterns

### Testing Standards
- `testing/test-writing.md` - Test structure and coverage

## Development Workflow

1. **Product Planning** → Creates mission.md, roadmap.md, tech-stack.md
2. **Spec Creation** → Documents feature requirements and design
3. **Task Breakdown** → Converts spec into actionable implementation tasks
4. **Implementation** → Builds feature following standards
5. **Verification** → Tests, validates, documents completion

## Instructions for AI Agents

When implementing features:

1. **Read Standards First**: Check relevant `agent-os/standards/` files before coding
2. **Follow Workflow**: Use the appropriate workflow from `agent-os/commands/`
3. **Specs Before Code**: Always create specification before implementation
4. **Atomic Tasks**: Break work into small, verifiable chunks
5. **Test Everything**: Write tests, run tests, validate results
6. **Truth-First**: Be honest about limitations, failures, and uncertainties

## Project-Specific Requirements

### Soap Calculator Domain Knowledge
- Saponification calculations (NaOH/KOH lye requirements)
- Oil/fat SAP values and fatty acid profiles
- Quality metrics: Hardness, Cleansing, Conditioning, Bubbly, Creamy
- Iodine values and INS calculations
- **Novel Feature**: Additive quality impact (clays, salts, botanicals)

### Research References
- Analysis document: `open-source-soap-calculator-analysis.md`
- Reference materials: `reference/` directory
- Existing calculators reviewed: Soapee, SoapMetrics, saponiCalc

### Critical Gap
**NO existing calculator** (open source or commercial) properly handles additive quality impact. This is the core differentiator for MGA's calculator.
