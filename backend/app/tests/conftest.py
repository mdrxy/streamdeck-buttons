"""
Configuration for pytest.
"""

from collections.abc import Generator

import pytest
from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import Button, User
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers, patch_password_hashing
from fastapi.testclient import TestClient
from sqlmodel import Session, delete


@pytest.fixture(scope="session")
def disable_password_hashing() -> Generator[None, None, None]:
    """
    Disable password hashing for the entire test session. This is
    useful for testing purposes, as it allows us to compare
    passwords directly without hashing them.
    """
    with patch_password_hashing("app.core.security"):
        yield


@pytest.fixture(scope="session", autouse=True)
def db(
    disable_password_hashing: Generator[  # pylint: disable=redefined-outer-name, unused-argument
        None, None, None
    ],
) -> Generator[Session, None, None]:
    """
    Get a database session for the entire test session. All tests will
    share the same database session.
    """
    with Session(engine) as session:
        # Clear the database before running tests. This ensures that
        # each test starts with a clean state.
        session.exec(delete(User))
        session.exec(delete(Button))
        session.commit()

        init_db(session)
        yield session
        statement = delete(Button)
        session.exec(statement)
        statement = delete(User)
        session.exec(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    Get a TestClient for the FastAPI app. This client will be used
    to make requests to the API during testing.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(
    client: TestClient,  # pylint: disable=redefined-outer-name
) -> dict[str, str]:
    """
    Fixture to get the token headers for the superuser.
    """
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(
    client: TestClient, db: Session  # pylint: disable=redefined-outer-name
) -> dict[str, str]:
    """
    Fixture to get the token headers for a normal user.
    """
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
