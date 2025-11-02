"""Add updated_at triggers and confidence_level constraint

Revision ID: 002
Revises: 001
Create Date: 2025-11-02 00:15:00

This migration addresses Phase 1 code review findings:
1. Adds PostgreSQL triggers for auto-updating updated_at columns
2. Adds CHECK constraint for confidence_level enum validation
3. Adds comment to hashed_password field documenting bcrypt requirement

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create trigger function for auto-updating updated_at timestamps
    # This function will be reused for all tables
    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """)

    # Add trigger to users table
    op.execute("""
    CREATE TRIGGER update_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    # Add trigger to oils table
    op.execute("""
    CREATE TRIGGER update_oils_updated_at
        BEFORE UPDATE ON oils
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    # Add trigger to additives table
    op.execute("""
    CREATE TRIGGER update_additives_updated_at
        BEFORE UPDATE ON additives
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    # Add CHECK constraint for confidence_level enum
    op.execute("""
    ALTER TABLE additives
    ADD CONSTRAINT confidence_level_check
    CHECK (confidence_level IN ('high', 'medium', 'low'));
    """)

    # Add comment to hashed_password field documenting security requirement
    op.execute("""
    COMMENT ON COLUMN users.hashed_password IS
    'MUST be bcrypt hash format ($2b$ prefix). Use passlib.hash.bcrypt.hash() to hash passwords.';
    """)


def downgrade() -> None:
    # Remove comment from hashed_password
    op.execute("COMMENT ON COLUMN users.hashed_password IS NULL;")

    # Remove CHECK constraint
    op.execute("ALTER TABLE additives DROP CONSTRAINT IF EXISTS confidence_level_check;")

    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_additives_updated_at ON additives;")
    op.execute("DROP TRIGGER IF EXISTS update_oils_updated_at ON oils;")
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users;")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
