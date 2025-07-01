from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from fastapi_do_zero.app import app
from fastapi_do_zero.database import get_session
from fastapi_do_zero.models import User, table_registry
from fastapi_do_zero.security import get_password_hash
from fastapi_do_zero.settings import Settings


@pytest.fixture
def settings():
    """
    Fixture to provide application settings for testing.
    This can be used to override settings in tests if needed.
    """
    return Settings()


@pytest.fixture
def token(client, user):
    """
    Fixture to create a JWT token for the user created in the `user` fixture.
    This token will be used in tests that require authentication.
    """
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )
    return response.json()['access_token']


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    """
    Fixture to create a user in the database for testing purposes.
    This user will be used in tests that require a user to be present.
    """
    password = 'testtest'
    user = User(
        username='test',
        email='test@test.com',
        password=get_password_hash(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password  # Store the plain password for tests

    return user


@pytest.fixture
def client(session):
    """
    Fixture to create a TestClient for the FastAPI application.
    This allows us to use the client in our tests without needing to
    instantiate it multiple times.
    """

    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def mock_db_time():
    """
    Fixture to mock the database time for testing purposes.
    It sets a fixed time for the `created_at` field in the User model.
    """
    return _mock_db_time


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)
