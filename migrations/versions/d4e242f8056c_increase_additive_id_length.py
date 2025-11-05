"""increase_additive_id_length

Revision ID: d4e242f8056c
Revises: 006
Create Date: 2025-11-05 08:51:33.806613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4e242f8056c'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Increase additive ID column length from 50 to 100 chars
    # Required for long additive names like "seeds_apricot_kernel,__blueberry,__cranberry,__raspberry"
    op.alter_column('additives', 'id',
                   existing_type=sa.String(length=50),
                   type_=sa.String(length=100),
                   existing_nullable=False)


def downgrade() -> None:
    # Revert additive ID column length to 50 chars
    op.alter_column('additives', 'id',
                   existing_type=sa.String(length=100),
                   type_=sa.String(length=50),
                   existing_nullable=False)
