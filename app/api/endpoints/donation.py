"""Отправка пожертвований и просмотр своих или всех перечислений."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.models.donation import Donation
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investment import invest_donations

router = APIRouter(prefix='/donation', tags=['donations'])


@router.get('/', response_model=List[DonationFullInfoDB],
            response_model_exclude_none=True,
            summary='Получить все пожертвования (суперпользователь)',
            description='Показать все пожертвования с распределёнными суммами.')
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
):
    result = await session.execute(select(Donation).order_by(Donation.id))
    return result.scalars().all()


@router.get('/my', response_model=List[DonationDB],
            response_model_exclude_none=True,
            summary='Получить свои пожертвования',
            description='История пожертвований текущего пользователя.')
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    result = await session.execute(
        select(Donation).where(Donation.user_id == user.id).order_by(Donation.id)
    )
    return result.scalars().all()


@router.post('/', response_model=DonationDB,
             response_model_exclude_none=True,
             summary='Сделать пожертвование',
             description='Перечислить сумму фонду с FIFO-распределением.')
async def create_donation(
    donation_data: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    donation = Donation(
        **donation_data.model_dump(),
        user_id=user.id,
    )
    session.add(donation)
    try:
        await session.flush()
        await invest_donations(session)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return donation
