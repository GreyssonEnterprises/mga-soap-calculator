# MGA Soap Calculator API

## Overview

The Core Soap Calculation API provides comprehensive soap recipe calculations for professional soap makers, including saponification values, quality metrics, fatty acid profiles, and industry-first additive effect modeling.

## Features

- **Dual Lye Support**: NaOH and KOH calculations with mixed lye ratios
- **Three Water Calculation Methods**: Water as % of oils, lye concentration, water:lye ratio
- **Complete Quality Metrics**: Hardness, cleansing, conditioning, bubbly lather, creamy lather, longevity, stability
- **Additive Effect Modeling**: First calculator to predict how clays, salts, botanicals affect soap quality
- **Fatty Acid Profiles**: Complete breakdown with sat:unsat ratios
- **JWT Authentication**: Secure user-specific calculations

## Tech Stack

- Python 3.11+
- FastAPI (async web framework)
- PostgreSQL 15+ with SQLAlchemy 2.0 (async)
- Alembic (migrations)
- JWT authentication
- pytest (TDD methodology)

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker (recommended for local development)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd mga-soap-calculator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment configuration
cp .env.example .env
# Edit .env with your database credentials

# Start PostgreSQL (Docker)
docker-compose up -d

# Run database migrations
alembic upgrade head

# Load seed data
python scripts/seed_database.py

# Run tests
pytest

# Start development server
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Project Structure

```
mga-soap-calculator/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Configuration
│   ├── db/           # Database setup
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── tests/
│   ├── unit/         # Unit tests
│   ├── integration/  # Integration tests
│   └── e2e/          # End-to-end tests
├── migrations/       # Alembic migrations
├── scripts/          # Utility scripts
└── reference/        # Documentation and research

## Development

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit

# With coverage report
pytest --cov=app --cov-report=html
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base
```

## License

Proprietary - MGA Automotive

## Authors

- Backend Architect Agent (Phase 1 Implementation)
- Spec Writer Agent (Specification)
- Deep Research Agent (Additive Effects Research)
