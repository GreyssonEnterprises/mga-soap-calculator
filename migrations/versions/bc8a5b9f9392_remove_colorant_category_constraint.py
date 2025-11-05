"""remove_colorant_category_constraint

Revision ID: bc8a5b9f9392
Revises: 21ba28925bc0
Create Date: 2025-11-05 08:56:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bc8a5b9f9392'
down_revision: Union[str, None] = '21ba28925bc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove the check constraint on color_category column
    op.drop_constraint('check_colorant_color_category_valid', 'colorants', type_='check')


def downgrade() -> None:
    # Re-create the check constraint with all valid categories including black_gray
    op.create_check_constraint(
        'check_colorant_color_category_valid',
        'colorants',
        "color_category IN ('yellow', 'orange', 'pink', 'red', 'purple', 'blue', 'brown', 'green', 'white', 'black', 'black_gray')"
    )
