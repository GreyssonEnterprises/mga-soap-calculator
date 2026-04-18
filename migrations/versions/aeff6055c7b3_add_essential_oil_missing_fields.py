"""add_essential_oil_missing_fields

Revision ID: aeff6055c7b3
Revises: d4e242f8056c
Create Date: 2025-11-05 08:53:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "aeff6055c7b3"
down_revision: str | None = "d4e242f8056c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add missing fields to essential_oils table
    op.add_column(
        "essential_oils",
        sa.Column(
            "usage_notes", sa.Text(), nullable=True, comment="Usage guidance and historical context"
        ),
    )
    op.add_column(
        "essential_oils",
        sa.Column(
            "color_effect",
            sa.String(length=200),
            nullable=True,
            comment="Expected color impact on soap",
        ),
    )

    # Change warnings from ARRAY to String
    op.alter_column(
        "essential_oils",
        "warnings",
        existing_type=postgresql.ARRAY(sa.String()),
        type_=sa.String(length=500),
        existing_nullable=True,
        existing_comment="Safety warnings: fades quickly, accelerates trace, skin sensitivity, photosensitivity",
    )


def downgrade() -> None:
    # Revert changes
    op.alter_column(
        "essential_oils",
        "warnings",
        existing_type=sa.String(length=500),
        type_=postgresql.ARRAY(sa.String()),
        existing_nullable=True,
        existing_comment="Safety warnings: fades quickly, accelerates trace, skin sensitivity, photosensitivity",
    )

    op.drop_column("essential_oils", "color_effect")
    op.drop_column("essential_oils", "usage_notes")
