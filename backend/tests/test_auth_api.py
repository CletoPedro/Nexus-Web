"""
Auth API tests, run against the real Postgres database and the real
bcrypt/JWT implementation — no mocking of hashing or token verification.
"""
from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD


def test_login_with_correct_credentials_succeeds(anon_client):
    resp = anon_client.post(
        "/api/v1/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == TEST_USER_EMAIL
    assert "hashed_password" not in body
    assert "password" not in body
    # Session cookie is set, httpOnly, never exposed as a token in the body.
    assert "nexus_session" in resp.cookies


def test_login_with_wrong_password_fails(anon_client):
    resp = anon_client.post(
        "/api/v1/auth/login",
        json={"email": TEST_USER_EMAIL, "password": "definitely-wrong-password"},
    )
    assert resp.status_code == 422
    assert "nexus_session" not in resp.cookies


def test_login_with_nonexistent_email_fails_identically(anon_client):
    """Same error for 'no such user' and 'wrong password' — never reveal which."""
    resp = anon_client.post(
        "/api/v1/auth/login",
        json={"email": "no-such-user@example.com", "password": "whatever123"},
    )
    assert resp.status_code == 422
    wrong_password_resp = anon_client.post(
        "/api/v1/auth/login",
        json={"email": TEST_USER_EMAIL, "password": "wrong"},
    )
    assert resp.json()["message"] == wrong_password_resp.json()["message"]


def test_me_requires_authentication(anon_client):
    resp = anon_client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user_when_authenticated(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == TEST_USER_EMAIL


def test_logout_clears_session(anon_client):
    login_resp = anon_client.post(
        "/api/v1/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    assert login_resp.status_code == 200
    assert anon_client.get("/api/v1/auth/me").status_code == 200

    logout_resp = anon_client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 204

    resp_after_logout = anon_client.get("/api/v1/auth/me")
    assert resp_after_logout.status_code == 401


def test_invalid_session_cookie_is_rejected(anon_client):
    anon_client.cookies.set("nexus_session", "not-a-real-jwt-token")
    resp = anon_client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_tampered_session_cookie_is_rejected(client, anon_client):
    # Take a real, valid token and corrupt it — must still be rejected.
    real_cookie = client.cookies.get("nexus_session")
    assert real_cookie is not None
    tampered = real_cookie[:-4] + "abcd"
    anon_client.cookies.set("nexus_session", tampered)
    resp = anon_client.get("/api/v1/auth/me")
    assert resp.status_code == 401
