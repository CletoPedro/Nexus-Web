"""
Shared fixtures. W12 introduces authentication, so every existing test
now needs an authenticated client rather than a bare TestClient. Login
happens once per pytest session (via the real /auth/login endpoint,
against a real user created directly through UserService) and the same
TestClient instance (with its cookie jar) is reused across tests in a
module — this is the `client` fixture.

`other_client` is a second, independently-authenticated user, used
specifically for cross-user ownership isolation tests.

`anon_client` is a fresh, unauthenticated client, for testing the
"no session" paths (401s, login failures, etc).
"""
import asyncio

import pytest
from fastapi.testclient import TestClient

from app.db.session import async_session_factory
from app.main import app
from app.repositories.user_repository import PostgresUserRepository
from app.services.user_service import UserService

TEST_USER_EMAIL = "w12-test-user@example.com"
TEST_USER_PASSWORD = "TestPassword123!"

OTHER_USER_EMAIL = "w12-other-user@example.com"
OTHER_USER_PASSWORD = "OtherPassword123!"


def _run(coro):
    return asyncio.run(coro)


async def _ensure_user(email: str, password: str) -> None:
    async with async_session_factory() as session:
        repo = PostgresUserRepository(session)
        existing = await repo.get_by_email(email)
        if existing is None:
            service = UserService(repo)
            await service.create_user(email=email, password=password)


@pytest.fixture(scope="session")
def _authenticated_client() -> TestClient:
    _run(_ensure_user(TEST_USER_EMAIL, TEST_USER_PASSWORD))
    c = TestClient(app)
    resp = c.post(
        "/api/v1/auth/login", json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    assert resp.status_code == 200, resp.text
    return c


@pytest.fixture(scope="session")
def _other_authenticated_client() -> TestClient:
    _run(_ensure_user(OTHER_USER_EMAIL, OTHER_USER_PASSWORD))
    c = TestClient(app)
    resp = c.post(
        "/api/v1/auth/login", json={"email": OTHER_USER_EMAIL, "password": OTHER_USER_PASSWORD}
    )
    assert resp.status_code == 200, resp.text
    return c


@pytest.fixture
def client(_authenticated_client: TestClient) -> TestClient:
    return _authenticated_client


@pytest.fixture
def other_client(_other_authenticated_client: TestClient) -> TestClient:
    return _other_authenticated_client


@pytest.fixture
def anon_client() -> TestClient:
    return TestClient(app)
