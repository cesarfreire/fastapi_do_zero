from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_do_zero.database import get_session
from fastapi_do_zero.models import User
from fastapi_do_zero.schemas import (
    JWTToken,
)
from fastapi_do_zero.security import (
    create_access_token,
    verify_password,
)

auth_router = APIRouter(prefix='/auth', tags=['auth'])

Session = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@auth_router.post('/token', response_model=JWTToken, status_code=HTTPStatus.OK)
async def login_for_access_token(session: Session, form_data: OAuth2Form):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return JWTToken(
        access_token=access_token,
        token_type='Bearer',
    )
