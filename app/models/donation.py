"""Пожертвование пользователя в общий фонд."""

from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import InvestmentBase


class Donation(InvestmentBase):
    __tablename__ = 'donation'

    comment = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
