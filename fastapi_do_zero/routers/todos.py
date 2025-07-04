from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_do_zero.database import get_session
from fastapi_do_zero.exceptions.todo import TodoNotFoundException
from fastapi_do_zero.models import Todo, User
from fastapi_do_zero.schemas import (
    FilterTodoParams,
    Message,
    TodoListSchema,
    TodoPublicSchema,
    TodoSchema,
    TodoUpdateSchema,
)
from fastapi_do_zero.security import get_current_user

todos_router = APIRouter(prefix='/todos', tags=['todos'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@todos_router.get('/', response_model=TodoListSchema)
async def list_todos(
    session: Session,
    user: CurrentUser,
    todo_filter: Annotated[FilterTodoParams, Query()],
):
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter.description)
        )

    if todo_filter.state:
        query = query.filter(Todo.state == todo_filter.state)

    todos = await session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    )

    return {'todos': todos.all()}


@todos_router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=TodoPublicSchema
)
async def create_todo(
    todo: TodoSchema,
    user: CurrentUser,
    session: Session,
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo


@todos_router.patch('/{todo_id}', response_model=TodoPublicSchema)
async def patch_todo(
    todo_id: int, session: Session, user: CurrentUser, todo: TodoUpdateSchema
):
    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise TodoNotFoundException

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@todos_router.delete('/{todo_id}', response_model=Message)
async def delete_todo(todo_id: int, session: Session, user: CurrentUser):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not todo:
        raise TodoNotFoundException

    await session.delete(todo)
    await session.commit()

    return {'message': 'Task has been deleted successfully'}
