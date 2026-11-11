"""Общая абстрактная модель денежных поступлений и целевых сборов."""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer
from sqlalchemy.orm import declared_attr

from app.core.db import Base


class InvestmentBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0, nullable=False)
    fully_invested = Column(Boolean, default=False, nullable=False)
    create_date = Column(DateTime, default=datetime.now, nullable=False)
    close_date = Column(DateTime, nullable=True)

    @declared_attr
    def __table_args__(cls):
        """Создать собственные ограничения для каждой дочерней таблицы."""
        table_name = cls.__tablename__
        return (
            CheckConstraint(
                'full_amount > 0',
                name=f'ck_{table_name}_full_amount_positive',
            ),
            CheckConstraint(
                'invested_amount >= 0 AND invested_amount <= full_amount',
                name=f'ck_{table_name}_invested_amount_range',
            ),
        )

    def __repr__(self) -> str:
        """Показать ключевые поля модели для отладки."""
        return (
            f'{type(self).__name__}('
            f'id={self.id!r}, '
            f'full_amount={self.full_amount!r}, '
            f'invested_amount={self.invested_amount!r}, '
            f'fully_invested={self.fully_invested!r})'
        )
