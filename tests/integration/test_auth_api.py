"""Session endpoints over HTTP (spec 0002, AC-1…AC-6, AC-9)."""

from __future__ import annotations

from collections.abc import Callable

from fastapi.testclient import TestClient
from httpx import Response

from leave_manager.models import User, UserRole

CreateUser = Callable[..., User]

LOGIN = "/api/v1/auth/login"
ME = "/api/v1/auth/me"
LOGOUT = "/api/v1/auth/logout"
PASSWORD = "dogru-sifre"


def _login(
    client: TestClient, email: str = "ayse@example.com", password: str = PASSWORD
) -> Response:
    response: Response = client.post(LOGIN, json={"email": email, "password": password})
    return response


def test_login_then_me_returns_user_without_password(
    client: TestClient, create_user: CreateUser
) -> None:
    user = create_user(role=UserRole.MANAGER)

    login = _login(client)
    me = client.get(ME)

    assert login.status_code == 200
    assert me.status_code == 200
    for body in (login.json(), me.json()):
        assert body["name"] == "Ayşe Yılmaz"
        assert body["email"] == "ayse@example.com"
        assert body["role"] == "Manager"
        assert set(body) == {"name", "email", "role", "csrf_token"}
    for text in (login.text, me.text):
        assert PASSWORD not in text
        assert user.password_hash not in text
        assert "argon2" not in text


def test_login_again_replaces_session(client: TestClient, create_user: CreateUser) -> None:
    create_user()
    create_user(email="mehmet@example.com", name="Mehmet Demir", role=UserRole.HR)

    _login(client)
    _login(client, email="mehmet@example.com")

    me = client.get(ME).json()
    assert (me["email"], me["role"]) == ("mehmet@example.com", "HR")


def test_login_accepts_mixed_case_padded_email(client: TestClient, create_user: CreateUser) -> None:
    create_user()

    response = _login(client, email="  AYSE@Example.Com  ")

    assert response.status_code == 200
    assert client.get(ME).json()["email"] == "ayse@example.com"


def test_wrong_password_and_unknown_email_return_identical_401(
    client: TestClient, create_user: CreateUser
) -> None:
    create_user()

    wrong_password = _login(client, password="yanlis-sifre")
    unknown_email = _login(client, email="kimse@example.com")

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert "lm_session" not in wrong_password.headers.get("set-cookie", "")
    assert client.get(ME).status_code == 401


def test_me_without_or_with_tampered_cookie_returns_401(
    client: TestClient, create_user: CreateUser
) -> None:
    create_user()

    anonymous = client.get(ME)
    _login(client)
    token = client.cookies["lm_session"]
    client.cookies.set("lm_session", token[:-3] + "AAA")
    tampered = client.get(ME)

    for response in (anonymous, tampered):
        assert response.status_code == 401
        assert response.json() == {
            "error": {"code": "NOT_LOGGED_IN", "message": "Oturum açılmamış."}
        }


def test_logout_ends_session(client: TestClient, create_user: CreateUser) -> None:
    create_user()
    csrf = _login(client).json()["csrf_token"]

    response = client.post(LOGOUT, headers={"X-CSRF-Token": csrf})

    assert response.status_code == 204
    assert "lm_session" in response.headers["set-cookie"]
    assert "Max-Age=0" in response.headers["set-cookie"]
    assert client.get(ME).status_code == 401


def test_logout_without_or_wrong_csrf_returns_403_and_keeps_session(
    client: TestClient, create_user: CreateUser
) -> None:
    create_user()
    csrf = _login(client).json()["csrf_token"]

    missing = client.post(LOGOUT)
    wrong = client.post(LOGOUT, headers={"X-CSRF-Token": csrf[:-1] + "x"})

    for response in (missing, wrong):
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "CSRF_TOKEN_INVALID"
        assert "set-cookie" not in response.headers
    assert client.get(ME).status_code == 200


def test_logout_without_session_returns_401(client: TestClient) -> None:
    response = client.post(LOGOUT, headers={"X-CSRF-Token": "anything"})

    assert response.status_code == 401


def test_login_needs_no_csrf_token(client: TestClient, create_user: CreateUser) -> None:
    create_user()

    response = client.post(LOGIN, json={"email": "ayse@example.com", "password": PASSWORD})

    assert "X-CSRF-Token" not in response.request.headers
    assert response.status_code == 200


def test_session_cookie_flags(client: TestClient, create_user: CreateUser) -> None:
    create_user()

    cookie = _login(client).headers["set-cookie"]

    attributes = [part.strip().lower() for part in cookie.split(";")]
    assert "httponly" in attributes
    assert "samesite=lax" in attributes
    assert "path=/" in attributes
    assert "max-age=28800" in attributes
    assert "secure" not in attributes


def test_session_cookie_secure_when_configured(
    secure_client: TestClient, create_user: CreateUser
) -> None:
    create_user()

    cookie = _login(secure_client).headers["set-cookie"]

    assert "secure" in [part.strip().lower() for part in cookie.split(";")]


def test_health_and_index_need_no_session(client: TestClient) -> None:
    assert "lm_session" not in client.cookies

    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/").status_code == 200
