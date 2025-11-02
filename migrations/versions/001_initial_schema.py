"""Initial schema: users, oils, additives, calculations

Revision ID: 001
Revises:
Create Date: 2025-11-01 16:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create oils table
    op.create_table(
        'oils',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('common_name', sa.String(100), nullable=False),
        sa.Column('inci_name', sa.String(200), nullable=False),
        sa.Column('sap_value_naoh', sa.Float, nullable=False, comment='Grams NaOH per gram of oil'),
        sa.Column('sap_value_koh', sa.Float, nullable=False, comment='Grams KOH per gram of oil'),
        sa.Column('iodine_value', sa.Float, nullable=False, comment='Measure of unsaturation'),
        sa.Column('ins_value', sa.Float, nullable=False, comment='Iodine Number Saponification (hardness indicator)'),
        sa.Column('fatty_acids', postgresql.JSONB, nullable=False, comment='Percentages of 8 fatty acids'),
        sa.Column('quality_contributions', postgresql.JSONB, nullable=False, comment='Contribution to 7 quality metrics'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create additives table
    op.create_table(
        'additives',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('common_name', sa.String(100), nullable=False),
        sa.Column('inci_name', sa.String(200), nullable=False),
        sa.Column('typical_usage_min_percent', sa.Float, nullable=False, comment='Minimum recommended usage as % of oil weight'),
        sa.Column('typical_usage_max_percent', sa.Float, nullable=False, comment='Maximum recommended usage as % of oil weight'),
        sa.Column('quality_effects', postgresql.JSONB, nullable=False, comment='Absolute modifiers to quality metrics at 2% usage'),
        sa.Column('confidence_level', sa.String(20), nullable=False, comment='Research confidence: high, medium, low'),
        sa.Column('verified_by_mga', sa.Boolean, nullable=False, server_default='false', comment='Whether MGA has empirically validated effects'),
        sa.Column('safety_warnings', postgresql.JSONB, nullable=True, comment='Optional safety information and usage notes'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create calculations table
    op.create_table(
        'calculations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recipe_data', postgresql.JSONB, nullable=False, comment='Complete recipe input'),
        sa.Column('results_data', postgresql.JSONB, nullable=False, comment='Complete calculation results'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_calculations_user_id', 'calculations', ['user_id'])
    op.create_index('ix_calculations_created_at', 'calculations', ['created_at'])
    op.create_index('ix_calculations_user_id_created_at', 'calculations', ['user_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_calculations_user_id_created_at', table_name='calculations')
    op.drop_index('ix_calculations_created_at', table_name='calculations')
    op.drop_index('ix_calculations_user_id', table_name='calculations')
    op.drop_table('calculations')
    op.drop_table('additives')
    op.drop_table('oils')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
