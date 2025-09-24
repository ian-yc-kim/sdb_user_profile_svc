"""create user_profile table

Revision ID: 97214870544a
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func


# revision identifiers, used by Alembic.
revision = '97214870544a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_profile table with CHECK constraint defined inline
    op.create_table('user_profile',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=6), nullable=False),
        sa.Column('region', sa.String(length=10), nullable=False),
        sa.Column('company', sa.String(length=10), nullable=True),
        sa.Column('bio', sa.String(length=128), nullable=True),
        sa.Column('hobbies', sa.String(length=10), nullable=True),
        sa.Column('interests', sa.Text(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.CheckConstraint('age >= 0 AND age <= 200', name='chk_user_profile_age_range')
    )
    
    # Create indexes
    op.create_index('idx_user_profile_name', 'user_profile', ['name'], unique=False)
    op.create_index('idx_user_profile_region', 'user_profile', ['region'], unique=False)
    op.create_index('ix_user_profile_id', 'user_profile', ['id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_user_profile_id', table_name='user_profile')
    op.drop_index('idx_user_profile_region', table_name='user_profile')
    op.drop_index('idx_user_profile_name', table_name='user_profile')
    
    # Drop table (this will also drop the CHECK constraint)
    op.drop_table('user_profile')
