from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_do_zero.database import get_session
from fastapi_do_zero.exceptions.auth import CredentialsException
from fastapi_do_zero.models import User
from fastapi_do_zero.settings import Settings

pwd_context = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/auth/token', refreshUrl='/auth/refresh'
)

settings = Settings()


def get_password_hash(password: str) -> str:
    """
    Hash a password using the recommended algorithm.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token with the given data.
    """
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('America/Sao_Paulo')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp': expire})
    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
) -> dict:
    """
    Decode the JWT token and return the user data.
    """
    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject_email = payload.get('sub')
        if not subject_email:
            raise CredentialsException
    except DecodeError:
        raise CredentialsException
    except ExpiredSignatureError:
        raise CredentialsException

    user = await session.scalar(
        select(User).where(User.email == subject_email)
    )

    if not user:
        raise CredentialsException

    return user
