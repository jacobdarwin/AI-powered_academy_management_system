from datetime import datetime, timedelta, timezone
import re

import jwt
import pytest
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import PasswordResetToken, User
from tests.route_role_matrix import build_matrix


def _path(rule):
    return re.sub(r"<int:[^>]+>", "1", rule).replace("<role>", "student")


def _request(client, method, path, headers=None):
    if path.endswith("/attendance") and method == "GET":
        path += "?batch_id=1"
    elif path.endswith("/attendance/monthly-summary") and method == "GET":
        path += "?batch_id=1&month=2026-11"
    kwargs = {"headers": headers or {}}
    if method in {"POST", "PATCH", "PUT"}:
        kwargs["json"] = {}
    return client.open(path, method=method, **kwargs)


def test_protected_routes_reject_missing_tokens(client, app):
    protected = [row for row in build_matrix(app) if row["allowed_roles"]]
    for row in protected:
        response = _request(client, row["method"], _path(row["path"]))
        assert response.status_code in {401, 422}, (
            row["method"], row["path"], response.status_code, response.get_json()
        )


def test_route_role_matrix_enforces_forbidden_roles(client, app, actors, auth_headers):
    for row in build_matrix(app):
        if not row["allowed_roles"]:
            continue
        for role in ("superadmin", "staff", "student"):
            path = _path(row["path"]).replace("/dashboard/student", f"/dashboard/{role}")
            login_id = "admin@example.com" if role == "superadmin" else (
                "STF-PLACEMENT" if role == "staff" and row["endpoint"].startswith("api.placements.") else (
                    "STF-ACCOUNTS" if role == "staff" and row["endpoint"].startswith("api.fees.") else (
                        "STF-COUNSELOR" if role == "staff" and row["endpoint"].startswith("api.leads.") else (
                            "STF-TRAINER-A" if role == "staff" else "STU-TEST-A"
                        )
                    )
                )
            )
            with app.app_context():
                user_id = 1 if role == "superadmin" else actors["users"][login_id]
                claims = {"role": role}
                if role == "staff":
                    claims["designation"] = "placement_officer" if login_id == "STF-PLACEMENT" else (
                        "accounts" if login_id == "STF-ACCOUNTS" else (
                            "counselor" if login_id == "STF-COUNSELOR" else "trainer"
                        )
                    )
                token_headers = {
                    "Authorization": f"Bearer {create_access_token(identity=str(user_id), additional_claims=claims)}"
                }
            response = _request(client, row["method"], path, token_headers)
            if role not in row["allowed_roles"]:
                assert response.status_code == 403, (
                    row["method"], row["path"], role, response.status_code,
                    response.get_json(),
                )
            else:
                assert response.status_code not in {401, 500}, (
                    row["method"], row["path"], role, response.status_code,
                    response.get_json(),
                )
            if row["endpoint"] == "api.auth.logout":
                auth_headers.clear()


def test_expired_malformed_wrong_key_and_tampered_tokens_are_rejected(client, app):
    with app.app_context():
        expired = create_access_token(
            identity="1", additional_claims={"role": "superadmin"},
            expires_delta=timedelta(seconds=-1),
        )
        wrong_key = jwt.encode(
            {
                "sub": "1",
                "type": "access",
                "role": "superadmin",
                "iat": datetime.now(timezone.utc),
                "nbf": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
                "jti": "wrong-key",
            },
            "wrong-key",
            algorithm="HS256",
        )
    tokens = [expired, "not-a-jwt", wrong_key, expired[:-1] + ("x" if expired[-1] != "x" else "y")]
    for token in tokens:
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in {401, 422}, response.get_json()


def test_inactive_and_locked_users_cannot_login(client, actors):
    inactive = client.post(
        "/api/v1/auth/login",
        json={"role": "student", "userId": "STU-INACTIVE", "password": actors["password"]},
    )
    locked = client.post(
        "/api/v1/auth/login",
        json={"role": "student", "userId": "STU-LOCKED", "password": actors["password"]},
    )
    assert inactive.status_code == 401
    assert locked.status_code == 401
    assert inactive.get_json()["message"] == locked.get_json()["message"] == "Invalid credentials"


def test_forgot_password_is_generic_and_reset_tokens_are_single_use(client, app, monkeypatch):
    raw_token = "stage2-reset-token"
    monkeypatch.setattr("app.api.auth.secrets.token_urlsafe", lambda _: raw_token)
    existing = client.post(
        "/api/v1/auth/forgot-password",
        json={"identifier": "admin@example.com"},
    )
    missing = client.post(
        "/api/v1/auth/forgot-password",
        json={"identifier": "missing@example.com"},
    )
    assert existing.status_code == missing.status_code == 200
    assert existing.get_json()["message"] == missing.get_json()["message"]
    reset = client.post(
        "/api/v1/auth/reset-password",
        json={"token": raw_token, "password": "new-password-123"},
    )
    assert reset.status_code == 200
    reused = client.post(
        "/api/v1/auth/reset-password",
        json={"token": raw_token, "password": "another-password-123"},
    )
    assert reused.status_code == 400
    old_login = client.post(
        "/api/v1/auth/login",
        json={"role": "superadmin", "userId": "admin@example.com", "password": "password123"},
    )
    new_login = client.post(
        "/api/v1/auth/login",
        json={"role": "superadmin", "userId": "admin@example.com", "password": "new-password-123"},
    )
    assert old_login.status_code == 401
    assert new_login.status_code == 200
    with app.app_context():
        token = db.session.scalar(
            db.select(PasswordResetToken).where(PasswordResetToken.token_hash.is_not(None))
        )
        assert token.used_at is not None


def test_expired_reset_token_is_rejected(client, app, monkeypatch):
    raw_token = "expired-stage2-token"
    monkeypatch.setattr("app.api.auth.secrets.token_urlsafe", lambda _: raw_token)
    assert client.post(
        "/api/v1/auth/forgot-password", json={"identifier": "admin@example.com"}
    ).status_code == 200
    with app.app_context():
        token = db.session.scalar(
            db.select(PasswordResetToken).where(PasswordResetToken.token_hash.is_not(None))
        )
        token.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.session.commit()
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": raw_token, "password": "new-password-123"},
    )
    assert response.status_code == 400


def test_deactivated_user_token_is_rejected_by_me(client, app):
    login = client.post(
        "/api/v1/auth/login",
        json={"role": "superadmin", "userId": "admin@example.com", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.get_json()['data']['access_token']}"}
    with app.app_context():
        user = db.session.scalar(db.select(User).where(User.login_id == "admin@example.com"))
        user.is_active = False
        db.session.commit()
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


def test_deactivated_user_token_is_rejected_by_role_guard(client, app):
    login = client.post(
        "/api/v1/auth/login",
        json={"role": "superadmin", "userId": "admin@example.com", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.get_json()['data']['access_token']}"}
    with app.app_context():
        user = db.session.scalar(db.select(User).where(User.login_id == "admin@example.com"))
        user.is_active = False
        db.session.commit()
    response = client.get("/api/v1/protected/superadmin-check", headers=headers)
    assert response.status_code == 401
