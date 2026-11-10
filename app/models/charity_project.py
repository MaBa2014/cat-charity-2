"""Модель целевого благотворительного проекта."""

from sqlalchemy import Column, String, Text

from app.models.base import InvestmentBase


class CharityProject(InvestmentBase):
    __tablename__ = 'charityproject'

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
