"""Публичное чтение проектов и управление проектами суперпользователем."""

from datetime import datetime
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.models.charity_project import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment import invest_donations
from app.services.validators import (
    ensure_project_can_be_deleted,
    ensure_project_is_open,
    ensure_unique_project_name,
    get_project_or_404,
    validate_project_updates,
)

router = APIRouter(prefix='/charity_project', tags=['charity_projects'])


@router.get('/', response_model=List[CharityProjectDB],
            response_model_exclude_none=True,
            summary='Получить список целевых проектов',
            description='Показать список всех целевых проектов.')
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(CharityProject).order_by(CharityProject.id)
    )
    return result.scalars().all()


@router.post('/', response_model=CharityProjectDB,
             response_model_exclude_none=True,
             summary='Создать целевой проект',
             description='Открыть сбор средств на помощь котикам.',
             responses={
                 HTTPStatus.BAD_REQUEST: {
                     'description': 'Неуникальное название проекта',
                 },
             })
async def create_charity_project(
    project_data: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    await ensure_unique_project_name(project_data.name, session)
    project = CharityProject(**project_data.model_dump())
    session.add(project)
    try:
        await session.flush()
        await invest_donations(session)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return project


@router.patch('/{project_id}', response_model=CharityProjectDB,
              response_model_exclude_none=True,
              summary='Редактировать целевой проект',
              description='Нельзя изменить закрытый проект или уменьшить '
                          'сумму ниже уже полученной.',
              responses={
                  HTTPStatus.BAD_REQUEST: {
                      'description': 'Недопустимое изменение',
                  },
                  HTTPStatus.NOT_FOUND: {
                      'description': 'Проект не найден',
                  },
              })
async def update_charity_project(
    project_id: int,
    project_data: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    project = await get_project_or_404(project_id, session)
    ensure_project_is_open(project)
    updates = project_data.model_dump(exclude_unset=True)
    validate_project_updates(project, updates)
    if updates.get('name') is not None:
        await ensure_unique_project_name(
            updates['name'], session, exclude_id=project_id,
        )
    for field, value in updates.items():
        setattr(project, field, value)
    if project.full_amount == project.invested_amount:
        project.fully_invested = True
        project.close_date = datetime.now()
    await session.commit()
    return project


@router.delete('/{project_id}', response_model=CharityProjectDB,
               response_model_exclude_none=True,
               summary='Удалить неинвестированный проект',
               description='Удалить открытый проект без вложений.',
               responses={
                   HTTPStatus.BAD_REQUEST: {
                       'description': 'Проект уже получил средства',
                   },
                   HTTPStatus.NOT_FOUND: {
                       'description': 'Проект не найден',
                   },
               })
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    project = await get_project_or_404(project_id, session)
    ensure_project_can_be_deleted(project)
    await session.delete(project)
    await session.commit()
    return project
