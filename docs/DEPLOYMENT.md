# MGA Soap Calculator API - Deployment Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-02
**Target:** MGA Automotive Internal Deployment

## Overview

The Core Soap Calculation API is a production-ready FastAPI application that provides professional-grade soap recipe calculations with JWT authentication and advanced additive effect modeling.

**Features:**
- FastAPI for high-performance async API
- PostgreSQL for persistent storage
- JWT authentication with bcrypt password hashing
- 21 comprehensive tests with 80% code coverage
- Docker containerization for easy deployment
- Complete OpenAPI/Swagger documentation

## Prerequisites

### Local Development
- Python 3.11 or higher
- PostgreSQL 15+ (via Docker recommended)
- pip or poetry for dependency management
- Docker and Docker Compose (recommended)

### Production Deployment
- PostgreSQL 15+ database server
- Python 3.11+ runtime
- Environment with ports 8000 (API) available
- 2+ CPU cores, 2GB RAM minimum

## Quick Start (Docker)

### Step 1: Start the Complete Stack

```bash
# Clone the repository (if needed)
git clone <repo-url>
cd mga-soap-calculator

# Start PostgreSQL and API services
docker-compose up -d

# Wait for services to be ready (10-15 seconds)
sleep 15
```

### Step 2: Initialize the Database

```bash
# Run migrations and seed data
bash scripts/init_db.sh
```

### Step 3: Verify the API is Running

```bash
# Check health endpoint
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status":"healthy","version":"1.0.0","environment":"development"}
```

### Step 4: Create a Test User

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Response includes new user with id
```

### Step 5: Login and Get Token

```bash
# Login to receive JWT token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }' | jq -r '.access_token')

echo $TOKEN
```

### Step 6: Make Your First Calculation

```bash
# Calculate a soap recipe
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "oils": [
      {"id": 1, "percentage": 50},
      {"id": 2, "percentage": 30},
      {"id": 3, "percentage": 20}
    ],
    "lye": {"naoh_percent": 100, "koh_percent": 0},
    "water": {"method": "percent_of_oils", "value": 38},
    "superfat_percent": 5
  }'
```

## Local Development Setup

### Option A: Using Docker Compose (Recommended)

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional for dev)
# Start services
docker-compose up -d

# Run migrations
docker-compose exec api bash scripts/init_db.sh

# Run tests
docker-compose exec api pytest

# View logs
docker-compose logs -f api
```

### Option B: Native Python Setup

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"

# Create .env file
cp .env.example .env

# Set DATABASE_URL in .env
# Example: DATABASE_URL=postgresql://user:password@localhost:5432/soap_calculator

# Start PostgreSQL (must be running independently)
docker run -d \
  --name postgres \
  -e POSTGRES_USER=soap_user \
  -e POSTGRES_PASSWORD=soap_password \
  -e POSTGRES_DB=soap_calculator \
  -p 5432:5432 \
  postgres:15

# Run migrations
alembic upgrade head

# Load seed data
python scripts/seed_database.py

# Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql://soap_user:soap_password@postgres:5432/soap_calculator

# JWT Secret (generate: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your-super-secret-key-here

# Application
ENVIRONMENT=development  # development, staging, production
APP_NAME=MGA Soap Calculator API
APP_VERSION=1.0.0

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Server
HOST=0.0.0.0
PORT=8000
```

### Generating a Secure Secret Key

```bash
# Generate a cryptographically secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -hex 32
```

## Database Setup

### Automatic Setup (Recommended)

```bash
# Single command to setup everything
bash scripts/init_db.sh
```

### Manual Setup

```bash
# Step 1: Apply migrations
alembic upgrade head

# Step 2: Load oil and additive seed data
python scripts/seed_database.py

# Step 3: Verify setup
psql $DATABASE_URL -c "SELECT COUNT(*) FROM oils;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM additives;"
```

### Database Reset (Development Only)

```bash
# WARNING: This deletes all data
alembic downgrade base

# Recreate fresh
alembic upgrade head
python scripts/seed_database.py
```

## Running Tests

### All Tests with Coverage

```bash
# Run all tests with coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html
```

### Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/

# Specific test file
pytest tests/e2e/test_complete_flow.py

# Verbose output with print statements
pytest -v -s
```

## API Documentation

### Interactive API Docs (Swagger)

```
http://localhost:8000/docs
```

Navigate to view:
- All endpoints with parameters
- Request/response examples
- Try-it-out functionality
- Error code documentation

### Alternative Documentation (ReDoc)

```
http://localhost:8000/redoc
```

More detailed, formatted documentation (better for reading).

### OpenAPI JSON Schema

```
http://localhost:8000/openapi.json
```

Machine-readable OpenAPI specification for integration with tools.

## Deployment to Production

### Step 1: Prepare Environment

```bash
# On production server
export ENVIRONMENT=production
export SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL=postgresql://user:pass@db-server:5432/soap_prod
export ALLOWED_ORIGINS=https://yourdomain.com
```

### Step 2: Build Docker Image

```bash
# Build production image
docker build -t mga-soap-api:1.0.0 .

# Tag for registry (if using container registry)
docker tag mga-soap-api:1.0.0 registry.example.com/mga-soap-api:1.0.0
```

### Step 3: Push to Container Registry (If Applicable)

```bash
docker push registry.example.com/mga-soap-api:1.0.0
```

### Step 4: Deploy Container

```bash
# Using Docker
docker run -d \
  --name mga-soap-api \
  -e DATABASE_URL=$DATABASE_URL \
  -e SECRET_KEY=$SECRET_KEY \
  -e ENVIRONMENT=production \
  -p 8000:8000 \
  mga-soap-api:1.0.0

# Or using Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Step 5: Verify Deployment

```bash
# Check health
curl https://your-api.com/api/v1/health

# Check logs
docker logs mga-soap-api
```

## Staging Environment Deployment

### Setup Staging Database

```bash
# Create staging database
createdb -h staging-db-host -U postgres soap_calculator_staging

# Set environment
export DATABASE_URL=postgresql://staging_user:pass@staging-db:5432/soap_calculator_staging
```

### Deploy to Staging

```bash
# Clone and setup on staging server
git clone <repo-url>
cd mga-soap-calculator
cp .env.staging .env
docker-compose -f docker-compose.staging.yml up -d
bash scripts/init_db.sh
```

### Run Smoke Tests

```bash
# Quick validation that staging is working
curl http://staging-api:8000/api/v1/health

# Create test user and run basic calculation
python tests/smoke_tests.py
```

## Troubleshooting

### Database Connection Errors

**Error:** `could not translate host name "postgres" to address`

**Solution:** Ensure PostgreSQL container is running
```bash
docker ps | grep postgres
docker-compose up -d  # Restart if needed
```

**Error:** `database "soap_calculator" does not exist`

**Solution:** Run database initialization
```bash
bash scripts/init_db.sh
```

### Migration Issues

**Error:** `alembic.util.exc.CommandError`

**Solution:** Check migration version
```bash
alembic current
alembic history
alembic upgrade head  # Apply pending migrations
```

### JWT/Authentication Issues

**Error:** `401 Unauthorized`

**Cause:** Missing or invalid JWT token

**Solution:**
```bash
# Get new token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"password"}' | jq -r '.access_token')

# Use token in requests
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/calculate
```

**Error:** `403 Forbidden`

**Cause:** User trying to access another user's calculation

**Solution:** Only access calculations created by current user

### Performance Issues

**Slow API responses:**

1. Check database performance
```bash
# Connect to database
psql $DATABASE_URL

# Check indexes
SELECT * FROM pg_indexes WHERE tablename = 'calculations';

# Check slow queries
SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

2. Review logs for errors
```bash
docker logs -f api
```

3. Monitor resource usage
```bash
docker stats
```

## Monitoring & Maintenance

### Health Checks

```bash
# Automated health monitoring
watch -n 5 'curl -s http://localhost:8000/api/v1/health | jq .'
```

### Viewing Logs

```bash
# Docker logs
docker logs -f mga-soap-api

# Last 100 lines
docker logs --tail 100 mga-soap-api

# With timestamps
docker logs -f --timestamps mga-soap-api
```

### Database Maintenance

```bash
# Backup database
pg_dump $DATABASE_URL > backup.sql

# Restore from backup
psql $DATABASE_URL < backup.sql

# Vacuum and analyze (PostgreSQL optimization)
psql $DATABASE_URL -c "VACUUM ANALYZE;"
```

## Scaling Considerations

### Horizontal Scaling

To run multiple API instances:

```bash
# Update docker-compose to run multiple replicas
docker-compose up -d --scale api=3

# Or manually run multiple containers with different ports
docker run -d -p 8001:8000 mga-soap-api:1.0.0
docker run -d -p 8002:8000 mga-soap-api:1.0.0
docker run -d -p 8003:8000 mga-soap-api:1.0.0

# Use load balancer (nginx) to distribute traffic
```

### Database Connection Pooling

Current configuration uses SQLAlchemy's connection pooling. Adjust in `app/core/config.py`:

```python
DATABASE_POOL_SIZE = 20  # Increase for more concurrent connections
DATABASE_MAX_OVERFLOW = 10  # Additional connections when pool exhausted
```

## Security Checklist

- [ ] **SECRET_KEY:** Changed from default, generated securely
- [ ] **DATABASE_URL:** Using strong password, not hardcoded
- [ ] **ALLOWED_ORIGINS:** Limited to trusted domains
- [ ] **HTTPS:** Enabled in production (reverse proxy)
- [ ] **CORS:** Configured restrictively
- [ ] **JWT Expiry:** Set to 24 hours
- [ ] **Password Policy:** Enforced strong passwords
- [ ] **Database Backups:** Configured and tested
- [ ] **SSL/TLS:** Certificates valid and not self-signed
- [ ] **API Rate Limiting:** Consider implementing for production

## Updating the Application

### Zero-Downtime Deployment (Production)

```bash
# Build new image
docker build -t mga-soap-api:1.0.1 .

# Start new container with updated code
docker run -d --name mga-soap-api-new \
  -e DATABASE_URL=$DATABASE_URL \
  -p 8001:8000 \
  mga-soap-api:1.0.1

# Switch load balancer to new container
# ... (load balancer specific steps)

# Stop old container
docker stop mga-soap-api
docker rm mga-soap-api

# Rename new container
docker rename mga-soap-api-new mga-soap-api
```

### With Data Migrations

```bash
# Deploy new code
docker build -t mga-soap-api:1.0.1 .

# Run database migrations in container
docker run --rm \
  -e DATABASE_URL=$DATABASE_URL \
  mga-soap-api:1.0.1 \
  alembic upgrade head

# Deploy new containers with updated code
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

## Support & Documentation

- **API Docs:** `/docs` (Swagger) or `/redoc` (ReDoc)
- **Spec File:** See `agent-os/specs/2025-11-01-core-calculation-api/spec.md`
- **Tests:** Run `pytest --cov` for full test coverage report
- **Issues:** Check logs with `docker logs` or application error responses

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-02 | Initial production release |

## Next Steps

1. **Read API Documentation:** Navigate to `/docs` endpoint
2. **Review OpenAPI Spec:** `/openapi.json` for integration details
3. **Run Integration Tests:** `pytest tests/integration/`
4. **Monitor in Production:** Setup logging and alerts
5. **Plan Phase 2:** Fragrance calculations and INCI generator

---

**Last Updated:** 2025-11-02
**Maintained By:** MGA Automotive Development Team
