#!/bin/bash
# Docker Entrypoint Script for MGA Soap Calculator
# Handles database readiness, migrations, and automatic seed data loading
# Ensures idempotent startup: safe to restart without duplicating data

set -e  # Exit on error

echo "=========================================="
echo "MGA Soap Calculator - Container Startup"
echo "=========================================="
echo ""

# =============================================================================
# Step 1: Wait for PostgreSQL to be ready
# =============================================================================
echo "[1/4] Waiting for PostgreSQL database..."

# Extract database connection details from DATABASE_URL
# Format: postgresql+asyncpg://user:password@host:port/database
DB_HOST="${DATABASE_HOST:-localhost}"
DB_PORT="${DATABASE_PORT:-5432}"
DB_USER="${DATABASE_USER:-soap_user}"

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
        echo "✓ Database is ready"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "✗ Database not ready after ${MAX_RETRIES} attempts"
        echo "  Host: $DB_HOST:$DB_PORT"
        echo "  User: $DB_USER"
        exit 1
    fi

    echo "  Waiting for database... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo ""

# =============================================================================
# Step 2: Run database migrations
# =============================================================================
echo "[2/4] Running database migrations..."

if alembic upgrade head; then
    echo "✓ Migrations applied successfully"
else
    echo "✗ Migration failed"
    exit 1
fi

echo ""

# =============================================================================
# Step 3: Check if database needs seeding
# =============================================================================
echo "[3/4] Checking for seed data..."

# Python script to check if database has seed data
NEEDS_SEED=$(python3.11 << 'EOF'
import asyncio
import sys
import os

# Suppress SQLAlchemy logging for this check
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.models.oil import Oil
from app.models.additive import Additive

async def check_seed_needed():
    """Check if database has seed data"""
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            # Count oils
            oil_count = await session.scalar(select(func.count()).select_from(Oil))

            # Count additives
            additive_count = await session.scalar(select(func.count()).select_from(Additive))

            await engine.dispose()

            # Need seed if either table is empty
            needs_seed = (oil_count == 0 or additive_count == 0)

            if needs_seed:
                print(f"NEEDS_SEED|oils={oil_count},additives={additive_count}")
            else:
                print(f"HAS_DATA|oils={oil_count},additives={additive_count}")

            return needs_seed
    except Exception as e:
        # If check fails, assume we need to seed
        print(f"ERROR|{str(e)}", file=sys.stderr)
        print("NEEDS_SEED|error=true")
        return True

# Run the check
asyncio.run(check_seed_needed())
EOF
)

# Parse the result
SEED_STATUS=$(echo "$NEEDS_SEED" | cut -d'|' -f1)
SEED_INFO=$(echo "$NEEDS_SEED" | cut -d'|' -f2)

if [ "$SEED_STATUS" = "NEEDS_SEED" ]; then
    echo "  Database is empty ($SEED_INFO)"
    echo "  Loading seed data..."

    if python3.11 scripts/seed_database.py; then
        echo "✓ Seed data loaded successfully"
        echo "  - 11 oils added"
        echo "  - 14 additives added (including Shale-validated data)"
    else
        echo "✗ Seed data loading failed"
        exit 1
    fi
elif [ "$SEED_STATUS" = "HAS_DATA" ]; then
    echo "✓ Seed data already present ($SEED_INFO)"
    echo "  Skipping seed to prevent duplicates"
elif [ "$SEED_STATUS" = "ERROR" ]; then
    echo "⚠ Could not verify seed status: $SEED_INFO"
    echo "  Attempting to seed anyway..."

    if python3.11 scripts/seed_database.py; then
        echo "✓ Seed operation completed"
    else
        echo "✗ Seed operation failed"
        exit 1
    fi
else
    echo "⚠ Unknown seed status: $SEED_STATUS"
    echo "  Proceeding with caution..."
fi

echo ""

# =============================================================================
# Step 4: Start application
# =============================================================================
echo "[4/4] Starting MGA Soap Calculator API..."
echo "  Host: 0.0.0.0:8000"
echo "  Workers: 4"
echo "  Environment: ${ENVIRONMENT:-production}"
echo ""
echo "=========================================="
echo "Ready to accept requests"
echo "=========================================="
echo ""

# Execute the application with all arguments passed to the entrypoint
# Using exec to replace the shell process with uvicorn
# This ensures signals (SIGTERM, etc.) are properly handled
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    --access-log \
    --proxy-headers \
    --forwarded-allow-ips "*"
