"""Создать таблицы пользователей, проектов и пожертвований.

Revision ID: 0001_initial
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('hashed_password', sa.String(length=1024), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True)
    op.create_table(
        'charityproject',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_amount', sa.Integer(), nullable=False),
        sa.Column('invested_amount', sa.Integer(), nullable=False),
        sa.Column('fully_invested', sa.Boolean(), nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=False),
        sa.Column('close_date', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_charityproject_name', 'charityproject',
                    ['name'], unique=True)
    op.create_table(
        'donation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_amount', sa.Integer(), nullable=False),
        sa.Column('invested_amount', sa.Integer(), nullable=False),
        sa.Column('fully_invested', sa.Boolean(), nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=False),
        sa.Column('close_date', sa.DateTime(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('donation')
    op.drop_index('ix_charityproject_name', table_name='charityproject')
    op.drop_table('charityproject')
    op.drop_index('ix_user_email', table_name='user')
    op.drop_table('user')
