"""Add lye purity tracking columns

Revision ID: 003
Revises: 002
Create Date: 2025-11-04 15:52:51

BREAKING CHANGE: Default KOH purity changes from 100% to 90%

This migration adds purity tracking columns to the calculations table
for KOH/NaOH purity support. Existing calculations are tagged with
purity_assumed=true to indicate legacy 100% KOH assumption.

Safety: CHECK constraints enforce 50-100% range at database level.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add purity columns with safety constraints"""

    # Add KOH purity column (default 90% - BREAKING CHANGE)
    op.add_column(
        "calculations",
        sa.Column(
            "koh_purity",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            server_default="90.00",
            comment="KOH purity percentage (50-100). Default 90% reflects commercial grade.",
        ),
    )

    # Add NaOH purity column (default 100% - unchanged)
    op.add_column(
        "calculations",
        sa.Column(
            "naoh_purity",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            server_default="100.00",
            comment="NaOH purity percentage (50-100). Default 100% reflects commercial grade.",
        ),
    )

    # Add pure KOH equivalent tracking (calculated field)
    op.add_column(
        "calculations",
        sa.Column(
            "pure_koh_equivalent_g",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
            comment="Theoretical pure KOH amount before purity adjustment",
        ),
    )

    # Add pure NaOH equivalent tracking (calculated field)
    op.add_column(
        "calculations",
        sa.Column(
            "pure_naoh_equivalent_g",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
            comment="Theoretical pure NaOH amount before purity adjustment",
        ),
    )

    # Add migration tracking flag
    op.add_column(
        "calculations",
        sa.Column(
            "purity_assumed",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="True if purity was assumed (legacy recipe), false if explicitly set",
        ),
    )

    # Add CHECK constraint for KOH purity range (50-100%)
    op.create_check_constraint(
        "check_koh_purity_range", "calculations", "koh_purity >= 50 AND koh_purity <= 100"
    )

    # Add CHECK constraint for NaOH purity range (50-100%)
    op.create_check_constraint(
        "check_naoh_purity_range", "calculations", "naoh_purity >= 50 AND naoh_purity <= 100"
    )

    # Tag existing calculations as having assumed purity
    # (They used the old 100% KOH default)
    op.execute(
        """
        UPDATE calculations
        SET purity_assumed = true
        WHERE created_at < NOW()
        """
    )

    # Add indexes for purity-based queries
    op.create_index("ix_calculations_koh_purity", "calculations", ["koh_purity"])
    op.create_index("ix_calculations_purity_assumed", "calculations", ["purity_assumed"])


def downgrade() -> None:
    """Remove purity columns and constraints"""

    # Drop indexes
    op.drop_index("ix_calculations_purity_assumed", table_name="calculations")
    op.drop_index("ix_calculations_koh_purity", table_name="calculations")

    # Drop CHECK constraints
    op.drop_constraint("check_naoh_purity_range", "calculations", type_="check")
    op.drop_constraint("check_koh_purity_range", "calculations", type_="check")

    # Drop columns
    op.drop_column("calculations", "purity_assumed")
    op.drop_column("calculations", "pure_naoh_equivalent_g")
    op.drop_column("calculations", "pure_koh_equivalent_g")
    op.drop_column("calculations", "naoh_purity")
    op.drop_column("calculations", "koh_purity")
