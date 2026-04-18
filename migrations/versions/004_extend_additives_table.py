"""Extend additives table with smart calculator fields

Revision ID: 004
Revises: 003
Create Date: 2025-11-05 08:00:00

This migration adds smart calculator fields to the additives table:
- usage_rate_min_pct, usage_rate_max_pct, usage_rate_standard_pct
- when_to_add, preparation_instructions
- category (additive type classification)
- warnings (structured JSONB for specific warnings)

These fields enable the smart additive calculator to provide
usage guidance and preparation instructions.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add smart calculator fields to additives table"""

    # Add usage rate columns for calculator
    op.add_column(
        "additives",
        sa.Column(
            "usage_rate_min_pct",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment="Minimum usage percentage for calculator (light usage)",
        ),
    )

    op.add_column(
        "additives",
        sa.Column(
            "usage_rate_max_pct",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment="Maximum usage percentage for calculator (heavy usage)",
        ),
    )

    op.add_column(
        "additives",
        sa.Column(
            "usage_rate_standard_pct",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment="Standard recommended usage percentage for calculator",
        ),
    )

    # Add preparation and timing guidance
    op.add_column(
        "additives",
        sa.Column(
            "when_to_add",
            sa.String(200),
            nullable=True,
            comment="Timing guidance: to oils, to lye water, at trace, etc.",
        ),
    )

    op.add_column(
        "additives",
        sa.Column(
            "preparation_instructions",
            sa.String(500),
            nullable=True,
            comment="How to prepare additive before incorporation",
        ),
    )

    # Add category classification
    op.add_column(
        "additives",
        sa.Column(
            "category",
            sa.String(50),
            nullable=True,
            comment="Additive category: exfoliant, colorant, lather_booster, hardener, clay, botanical",
        ),
    )

    # Add structured warnings (replaces/complements safety_warnings)
    op.add_column(
        "additives",
        sa.Column(
            "warnings",
            JSONB,
            nullable=True,
            comment="Specific warnings: accelerates_trace, causes_overheating, can_be_scratchy, turns_brown",
        ),
    )

    # Add CHECK constraint for usage rate ordering (min <= standard <= max)
    op.create_check_constraint(
        "check_additive_usage_rate_ordering",
        "additives",
        "usage_rate_min_pct IS NULL OR usage_rate_max_pct IS NULL OR usage_rate_min_pct <= usage_rate_max_pct",
    )

    op.create_check_constraint(
        "check_additive_standard_in_range",
        "additives",
        "usage_rate_standard_pct IS NULL OR "
        "(usage_rate_min_pct IS NULL OR usage_rate_standard_pct >= usage_rate_min_pct) AND "
        "(usage_rate_max_pct IS NULL OR usage_rate_standard_pct <= usage_rate_max_pct)",
    )

    # Add index on category for filtering
    op.create_index("ix_additives_category", "additives", ["category"])


def downgrade() -> None:
    """Remove smart calculator fields from additives table"""

    # Drop index
    op.drop_index("ix_additives_category", table_name="additives")

    # Drop CHECK constraints
    op.drop_constraint("check_additive_standard_in_range", "additives", type_="check")
    op.drop_constraint("check_additive_usage_rate_ordering", "additives", type_="check")

    # Drop columns
    op.drop_column("additives", "warnings")
    op.drop_column("additives", "category")
    op.drop_column("additives", "preparation_instructions")
    op.drop_column("additives", "when_to_add")
    op.drop_column("additives", "usage_rate_standard_pct")
    op.drop_column("additives", "usage_rate_max_pct")
    op.drop_column("additives", "usage_rate_min_pct")
