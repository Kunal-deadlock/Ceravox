"""First-run setup and session authentication tests."""

from sqlalchemy import select

from app.db.models import SessionRecord, User

PASSWORD = "Correct-Horse-7!"  # pragma: allowlist secret


def csrf(client) -> str:
    response = client.get("/v1/auth/csrf")
    assert response.status_code == 200
    return response.json()["csrf_token"]


def setup_admin(client, email: str = "admin@example.test") -> None:
    token = csrf(client)
    response = client.post(
        "/v1/auth/setup",
        json={"email": email, "password": PASSWORD},
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 201


def login(client, email: str = "admin@example.test"):
    token = csrf(client)
    return client.post(
        "/v1/auth/login",
        json={"email": email, "password": PASSWORD},
        headers={"X-CSRF-Token": token},
    )


def test_first_run_setup_creates_exactly_one_admin(client, db_session) -> None:
    assert client.get("/v1/auth/status").json() == {"setup_required": True}
    setup_admin(client)

    assert client.get("/v1/auth/status").json() == {"setup_required": False}
    users = db_session.scalars(select(User)).all()
    assert len(users) == 1
    assert users[0].is_admin is True

    second = client.post(
        "/v1/auth/setup",
        json={"email": "other@example.test", "password": PASSWORD},
        headers={"X-CSRF-Token": csrf(client)},
    )
    assert second.status_code == 409
    assert len(db_session.scalars(select(User)).all()) == 1


def test_login_sets_hardened_cookie_and_stores_only_hashes(client, db_session) -> None:
    setup_admin(client)

    response = login(client)

    assert response.status_code == 200
    cookie = response.headers["set-cookie"]
    assert "ceravox_session=" in cookie
    assert "HttpOnly" in cookie
    assert "samesite=lax" in cookie.lower()
    raw_session_token = client.cookies.get("ceravox_session")
    stored = db_session.scalar(select(SessionRecord))
    assert stored is not None
    assert stored.token_hash != raw_session_token
    assert stored.token_hash.startswith("sha256$")

    user = db_session.scalar(select(User))
    assert user is not None
    assert user.password_hash.startswith("$argon2")
    assert PASSWORD not in user.password_hash


def test_invalid_login_is_generic(client) -> None:
    setup_admin(client)
    invalid_password = client.post(
        "/v1/auth/login",
        json={
            "email": "admin@example.test",
            "password": "wrong-password",  # pragma: allowlist secret
        },
        headers={"X-CSRF-Token": csrf(client)},
    )
    unknown_email = client.post(
        "/v1/auth/login",
        json={
            "email": "missing@example.test",
            "password": "wrong-password",  # pragma: allowlist secret
        },
        headers={"X-CSRF-Token": csrf(client)},
    )

    assert invalid_password.status_code == unknown_email.status_code == 401
    assert (
        invalid_password.json()
        == unknown_email.json()
        == {"error": {"code": "invalid_credentials", "message": "Invalid email or password"}}
    )


def test_me_requires_auth_and_returns_safe_profile(client) -> None:
    assert client.get("/v1/auth/me").status_code == 401
    setup_admin(client)
    assert login(client).status_code == 200

    response = client.get("/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.test"
    assert response.json()["is_admin"] is True
    assert "password_hash" not in response.json()
    assert "session_token" not in response.json()


def test_logout_invalidates_session(client) -> None:
    setup_admin(client)
    assert login(client).status_code == 200
    logout = client.post(
        "/v1/auth/logout",
        headers={"X-CSRF-Token": csrf(client)},
    )

    assert logout.status_code == 204
    assert client.get("/v1/auth/me").status_code == 401


def test_protected_route_rejects_anonymous_requests(client) -> None:
    assert client.get("/v1/app/status").status_code == 401


def test_register_creates_account_and_session(client, db_session) -> None:
    token = csrf(client)
    response = client.post(
        "/v1/auth/register",
        json={"email": "newuser@example.test", "password": PASSWORD},
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.test"
    assert "ceravox_session=" in response.headers["set-cookie"]

    # Verify protected route works with new session
    me = client.get("/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "newuser@example.test"
