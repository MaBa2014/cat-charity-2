"""Проверять допустимость сумм для проектов и пожертвований.

Revision ID: 0002_investment_constraints
Revises: 0001_initial
"""

from alembic import op

revision = '0002_investment_constraints'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    for table_name in ('charityproject', 'donation'):
        # SQLite не поддерживает ADD CONSTRAINT, поэтому Alembic
        # пересоздаёт таблицы с сохранением уже записанных данных.
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.create_check_constraint(
                f'ck_{table_name}_full_amount_positive',
                'full_amount > 0',
            )
            batch_op.create_check_constraint(
                f'ck_{table_name}_invested_amount_range',
                'invested_amount >= 0 AND invested_amount <= full_amount',
            )


def downgrade():
    for table_name in ('donation', 'charityproject'):
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.drop_constraint(
                f'ck_{table_name}_invested_amount_range',
                type_='check',
            )
            batch_op.drop_constraint(
                f'ck_{table_name}_full_amount_positive',
                type_='check',
            )
