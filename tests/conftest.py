import pytest
from fastapi.testclient import TestClient

from fastapi_do_zero.app import app


@pytest.fixture
def client():
    """
    Fixture to create a TestClient for the FastAPI application.
    This allows us to use the client in our tests without needing to
    instantiate it multiple times.
    """
    return TestClient(app)
