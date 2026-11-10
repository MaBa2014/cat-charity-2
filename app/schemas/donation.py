"""Схемы пожертвований с разным уровнем детализации."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, PositiveInt


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class DonationDB(DonationCreate):
    id: int
    create_date: datetime

    model_config = ConfigDict(from_attributes=True, extra='forbid')


class DonationFullInfoDB(DonationDB):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime] = None
