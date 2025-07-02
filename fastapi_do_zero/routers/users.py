from http import HTTPStatus
from logging import getLogger
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_do_zero.database import get_session
from fastapi_do_zero.exceptions.auth import PermissionException
from fastapi_do_zero.models import User
from fastapi_do_zero.schemas import (
    FilterParams,
    Message,
    UserListSchema,
    UserPublicSchema,
    UserSchema,
)
from fastapi_do_zero.security import get_current_user, get_password_hash

users_router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

logger = getLogger('uvicorn.error')


@users_router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=UserPublicSchema
)
async def create_user(user: UserSchema, session: Session):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        logger.warning(
            f'User with username {user.username} '
            f'or email {user.email} already exists.'
        )
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )

    db_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@users_router.get(
    '/', status_code=HTTPStatus.OK, response_model=UserListSchema
)
async def list_users(
    session: Session,
    current_user: CurrentUser,
    filter_users: Annotated[FilterParams, Query()],
):
    users = await session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
    )
    return {'users': users}


@users_router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise PermissionException

    try:
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email
        await session.commit()
        await session.refresh(current_user)
        return current_user
    except IntegrityError:
        logger.warning(
            f'Update failed for user {user_id} '
            f'due to duplicate username or email.'
        )
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )


@users_router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
async def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise PermissionException

    await session.delete(current_user)
    await session.commit()

    return Message(message='User deleted successfully')


@users_router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
async def read_user(user_id: int, session: Session):
    db_user = await session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        logger.warning(f'User with id {user_id} not found.')
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return db_user
