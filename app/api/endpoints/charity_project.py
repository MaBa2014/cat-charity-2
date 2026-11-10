"""Публичное чтение проектов и управление проектами суперпользователем."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
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

router = APIRouter(prefix='/charity_project', tags=['charity_projects'])


async def _get_project(project_id: int, session: AsyncSession) -> CharityProject:
    project = await session.get(CharityProject, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail='Проект не найден!')
    return project


async def _name_exists(
    name: str, session: AsyncSession, exclude_id: int = None,
) -> bool:
    statement = select(CharityProject.id).where(CharityProject.name == name)
    if exclude_id is not None:
        statement = statement.where(CharityProject.id != exclude_id)
    return (await session.execute(statement)).scalar_one_or_none() is not None


@router.get('/', response_model=List[CharityProjectDB],
            response_model_exclude_none=True,
            summary='Получить список целевых проектов',
            description='Показать список всех целевых проектов.')
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(CharityProject).order_by(CharityProject.id))
    return result.scalars().all()


@router.post('/', response_model=CharityProjectDB,
             response_model_exclude_none=True,
             summary='Создать целевой проект',
             description='Открыть сбор средств на помощь котикам.',
             responses={400: {'description': 'Неуникальное название проекта'}})
async def create_charity_project(
    project_data: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    if await _name_exists(project_data.name, session):
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )
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
              responses={400: {'description': 'Недопустимое изменение'},
                         404: {'description': 'Проект не найден'}})
async def update_charity_project(
    project_id: int,
    project_data: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    project = await _get_project(project_id, session)
    if project.fully_invested:
        raise HTTPException(status_code=400,
                            detail='Закрытый проект нельзя редактировать!')
    updates = project_data.model_dump(exclude_unset=True)
    if 'full_amount' in updates and updates['full_amount'] is not None:
        if updates['full_amount'] < project.invested_amount:
            raise HTTPException(
                status_code=400,
                detail='Нельзя установить сумму меньше уже вложенной!',
            )
    if updates.get('name') is not None and await _name_exists(
        updates['name'], session, exclude_id=project_id,
    ):
        raise HTTPException(status_code=400,
                            detail='Проект с таким именем уже существует!')
    for field, value in updates.items():
        # Pydantic допускает Optional; обязательные поля БД не обнуляем.
        if value is None:
            raise HTTPException(status_code=422,
                                detail=f'Поле {field} не может быть null')
        setattr(project, field, value)
    if project.full_amount == project.invested_amount:
        project.fully_invested = True
        project.close_date = datetime.now()
    await session.commit()
    return project


@router.delete('/{project_id}', response_model=CharityProjectDB,
               response_model_exclude_none=True,
               summary='Удалить неинвестированный проект',
               description='Удалить можно только открытый проект без вложений.',
               responses={400: {'description': 'Проект уже получил средства'},
                          404: {'description': 'Проект не найден'}})
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    project = await _get_project(project_id, session)
    if project.fully_invested or project.invested_amount:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!',
        )
    await session.delete(project)
    await session.commit()
    return project
