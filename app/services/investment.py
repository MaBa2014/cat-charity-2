"""FIFO-распределение пожертвований по открытым проектам.

Сервис не вызывает commit: создание записи и перераспределение денежных
средств должны подтверждаться одним commit на уровне API.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation


async def invest_donations(session: AsyncSession) -> None:
    """Распределить свободные суммы от старых пожертвований к старым проектам."""
    projects = (await session.execute(
        select(CharityProject)
        .where(CharityProject.fully_invested.is_(False))
        .order_by(CharityProject.create_date, CharityProject.id)
    )).scalars().all()
    donations = (await session.execute(
        select(Donation)
        .where(Donation.fully_invested.is_(False))
        .order_by(Donation.create_date, Donation.id)
    )).scalars().all()

    donation_index = 0
    for project in projects:
        while donation_index < len(donations):
            donation = donations[donation_index]
            to_invest = min(
                project.full_amount - project.invested_amount,
                donation.full_amount - donation.invested_amount,
            )
            if to_invest > 0:
                project.invested_amount += to_invest
                donation.invested_amount += to_invest

            if donation.invested_amount == donation.full_amount:
                donation.fully_invested = True
                donation.close_date = datetime.now()
                donation_index += 1

            if project.invested_amount == project.full_amount:
                project.fully_invested = True
                project.close_date = datetime.now()
                break

            # Для неконсистентных старых данных не допускаем зацикливания.
            if to_invest == 0 and not donation.fully_invested:
                break
