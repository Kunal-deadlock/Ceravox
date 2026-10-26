"""CSRF coverage for cookie-authenticated mutations."""

from .test_auth import PASSWORD, csrf


def test_setup_rejects_missing_csrf_token(client) -> None:
    client.get("/v1/auth/csrf")
    response = client.post(
        "/v1/auth/setup",
        json={"email": "admin@example.test", "password": PASSWORD},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_failed"


def test_login_rejects_mismatched_csrf_token(client) -> None:
    csrf(client)
    response = client.post(
        "/v1/auth/login",
        json={"email": "admin@example.test", "password": PASSWORD},
        headers={"X-CSRF-Token": "wrong-token"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_failed"
