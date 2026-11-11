"""Проверки бизнес-правил при работе с целевыми проектами."""

from http import HTTPStatus
from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject


async def get_project_or_404(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    """Найти проект или сообщить, что его не существует."""
    project = await session.get(CharityProject, project_id)
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!',
        )
    return project


async def ensure_unique_project_name(
    name: str,
    session: AsyncSession,
    exclude_id: Optional[int] = None,
) -> None:
    """Запретить совпадение имён разных проектов."""
    statement = select(CharityProject.id).where(CharityProject.name == name)
    if exclude_id is not None:
        statement = statement.where(CharityProject.id != exclude_id)
    result = await session.execute(statement)
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


def ensure_project_is_open(project: CharityProject) -> None:
    """Запретить редактирование закрытого проекта."""
    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )


def validate_project_updates(
    project: CharityProject,
    updates: Dict[str, Any],
) -> None:
    """Проверить изменение суммы и запретить обнуление полей."""
    for field, value in updates.items():
        if value is None:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=f'Поле {field} не может быть null',
            )

    new_amount = updates.get('full_amount')
    if new_amount is not None and new_amount < project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нельзя установить сумму меньше уже вложенной!',
        )


def ensure_project_can_be_deleted(project: CharityProject) -> None:
    """Запретить удаление закрытого проекта или проекта с вложениями."""
    if project.fully_invested or project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!',
        )
