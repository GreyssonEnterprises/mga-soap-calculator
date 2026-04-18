"""remove_essential_oil_note_constraint

Revision ID: 21ba28925bc0
Revises: b76343b095ad
Create Date: 2025-11-05 08:55:00

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "21ba28925bc0"
down_revision: str | None = "b76343b095ad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Remove the check constraint on note column
    op.drop_constraint("check_essential_oil_note_valid", "essential_oils", type_="check")


def downgrade() -> None:
    # Re-create the check constraint with updated values
    op.create_check_constraint(
        "check_essential_oil_note_valid",
        "essential_oils",
        "note IN ('Top', 'Middle', 'Base', 'Top, Middle, or Base (depends on blend)', 'Middle to Top')",  # noqa: E501
    )
