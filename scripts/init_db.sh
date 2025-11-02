#!/bin/bash

# Database Initialization Script for MGA Soap Calculator
# Initializes PostgreSQL database with schema, migrations, and seed data
# Usage: bash scripts/init_db.sh

set -e  # Exit on first error

echo "=========================================="
echo "MGA Soap Calculator - Database Initialization"
echo "=========================================="
echo ""

# Step 1: Check if running in Docker or locally
if [ -f /.dockerenv ]; then
    echo "[Docker] Running inside container"
    PYTHON_CMD="python"
else
    echo "[Local] Running on host system"
    PYTHON_CMD="python3"
fi

# Step 2: Apply Alembic migrations
echo ""
echo "Step 1/3: Running database migrations..."
alembic upgrade head
if [ $? -eq 0 ]; then
    echo "✓ Migrations applied successfully"
else
    echo "✗ Migration failed"
    exit 1
fi

# Step 3: Seed database with oils and additives
echo ""
echo "Step 2/3: Loading seed data..."
$PYTHON_CMD scripts/seed_database.py
if [ $? -eq 0 ]; then
    echo "✓ Seed data loaded successfully"
else
    echo "✗ Seed data loading failed"
    exit 1
fi

# Step 4: Verify data was loaded
echo ""
echo "Step 3/3: Verifying database..."
$PYTHON_CMD << 'EOF'
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, func

async def verify_db():
    """Verify that database has expected data."""
    db_url = os.getenv('DATABASE_URL', 'postgresql://soap_user:soap_password@localhost:5432/mga_soap_calculator')
    # Convert to async URL
    db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')

    engine = create_async_engine(db_url)

    async with engine.begin() as conn:
        # Count oils
        result = await conn.execute(select(func.count()).select_from(
            __import__('sqlalchemy').Table('oils', __import__('sqlalchemy').MetaData(), autoload_with=engine.sync_engine)
        ))
        oils_count = result.scalar()

        # Count additives
        result = await conn.execute(select(func.count()).select_from(
            __import__('sqlalchemy').Table('additives', __import__('sqlalchemy').MetaData(), autoload_with=engine.sync_engine)
        ))
        additives_count = result.scalar()

        print(f"Database Verification:")
        print(f"  Oils: {oils_count} entries")
        print(f"  Additives: {additives_count} entries")

        if oils_count >= 11 and additives_count >= 12:
            print(f"✓ Database initialized successfully!")
            return True
        else:
            print(f"✗ Insufficient data loaded")
            return False

    await engine.dispose()

# Run verification
success = asyncio.run(verify_db())
exit(0 if success else 1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Database initialization complete!"
    echo "=========================================="
    echo ""
    echo "API is ready. Start with:"
    echo "  docker-compose up -d"
    echo "  curl http://localhost:8000/api/v1/health"
    echo ""
    exit 0
else
    echo ""
    echo "Database verification failed"
    exit 1
fi
