"""increase_essential_oil_note_length

Revision ID: b76343b095ad
Revises: aeff6055c7b3
Create Date: 2025-11-05 08:54:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b76343b095ad'
down_revision: Union[str, None] = 'aeff6055c7b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Increase note column length from 20 to 50 chars
    # Required for notes like "Top, Middle, or Base (depends on blend)"
    op.alter_column('essential_oils', 'note',
                   existing_type=sa.String(length=20),
                   type_=sa.String(length=50),
                   existing_nullable=True,
                   existing_comment='Fragrance note: top, middle, or base')


def downgrade() -> None:
    # Revert note column length to 20 chars
    op.alter_column('essential_oils', 'note',
                   existing_type=sa.String(length=50),
                   type_=sa.String(length=20),
                   existing_nullable=True,
                   existing_comment='Fragrance note: top, middle, or base')
