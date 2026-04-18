"""add_saponified_inci_name_to_oils

Revision ID: 007
Revises: bc8a5b9f9392
Create Date: 2025-11-05

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: str | None = "bc8a5b9f9392"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add saponified_inci_name column to oils table"""
    op.add_column(
        "oils",
        sa.Column(
            "saponified_inci_name",
            sa.String(length=200),
            nullable=True,
            comment="Post-saponification INCI name (e.g., 'Sodium Cocoate' or 'Potassium Cocoate')",
        ),
    )


def downgrade() -> None:
    """Remove saponified_inci_name column from oils table"""
    op.drop_column("oils", "saponified_inci_name")
