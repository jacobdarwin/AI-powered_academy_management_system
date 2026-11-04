from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from flask import Blueprint, current_app, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from ..auth import authenticated
from ..extensions import db, limiter
from ..models import PasswordResetToken, RevokedToken, Staff, Student, User
from ..responses import failure, success

auth_api = Blueprint("auth", __name__, url_prefix="/auth")

GENERIC_LOGIN_ERROR = "Invalid credentials"
GENERIC_RESET_MESSAGE = "If an account matches the identifier, a reset link is on its way."


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _utc(value: datetime | None) -> datetime | None:
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _profile(user: User) -> dict:
    staff = db.session.scalar(db.select(Staff).where(Staff.user_id == user.id))
    student = db.session.scalar(db.select(Student).where(Student.user_id == user.id))
    profile = staff or student
    designation = staff.designation if staff else None
    name = profile.name if profile else user.email or user.login_id
    return {
        "id": user.id,
        "name": name,
        "role": user.role,
        "designation": designation,
        "login_id": user.login_id,
        "email": user.email,
        "must_change_password": user.must_change_password,
    }


def _tokens(user: User) -> dict:
    claims = {"role": user.role}
    staff = db.session.scalar(db.select(Staff).where(Staff.user_id == user.id))
    if staff:
        claims["designation"] = staff.designation
    return {
        "access_token": create_access_token(identity=str(user.id), additional_claims=claims),
        "refresh_token": create_refresh_token(identity=str(user.id), additional_claims=claims),
    }


@auth_api.post("/login")
@limiter.limit("10 per minute")
def login():
    body = request.get_json(silent=True) or {}
    role = str(body.get("role", "")).strip().lower()
    identifier = str(body.get("userId", "")).strip()
    password = body.get("password", "")
    if not role or not identifier or not isinstance(password, str):
        return failure(GENERIC_LOGIN_ERROR, 401)

    user = db.session.scalar(
        db.select(User).where(or_(User.login_id == identifier, User.email == identifier.lower()))
    )
    now = _now()
    if (
        user is None
        or user.role != role
        or not user.is_active
        or (_utc(user.locked_until) is not None and _utc(user.locked_until) > now)
        or not check_password_hash(user.password_hash, password)
    ):
        if user is not None and user.role == role and user.is_active:
            user.failed_login_count += 1
            if user.failed_login_count >= 5:
                user.locked_until = now + timedelta(minutes=15)
        db.session.commit()
        return failure(GENERIC_LOGIN_ERROR, 401)

    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = now
    db.session.commit()
    return success({**_tokens(user), "user": _profile(user)}, "Login successful")


@auth_api.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    claims = get_jwt()
    user = db.session.get(User, int(identity))
    if user is None or not user.is_active:
        return failure("Invalid refresh token", 401)
    return success(
        {
            "access_token": create_access_token(
                identity=identity,
                additional_claims={
                    "role": claims.get("role"),
                    "designation": claims.get("designation"),
                },
            )
        }
    )


@auth_api.post("/logout")
@jwt_required()
def logout():
    db.session.add(RevokedToken(jti=get_jwt()["jti"], revoked_at=_now()))
    db.session.commit()
    return success(message="Logged out")


@auth_api.get("/me")
@authenticated
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None or not user.is_active:
        return failure("Authentication required", 401)
    return success(_profile(user))


@auth_api.post("/change-password")
@authenticated
def change_password():
    body = request.get_json(silent=True) or {}
    current = body.get("current_password")
    new = body.get("new_password")
    if not isinstance(current, str) or not isinstance(new, str) or len(new) < 8:
        return failure("Validation failed", 422, {"new_password": ["Use at least 8 characters."]})
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None or not check_password_hash(user.password_hash, current):
        return failure("Current password is incorrect", 400)
    user.password_hash = generate_password_hash(new)
    user.must_change_password = False
    db.session.commit()
    return success(message="Password updated")


@auth_api.post("/forgot-password")
@limiter.limit("5 per minute")
def forgot_password():
    body = request.get_json(silent=True) or {}
    identifier = str(body.get("identifier", "")).strip()
    user = db.session.scalar(
        db.select(User).where(or_(User.login_id == identifier, User.email == identifier.lower()))
    )
    if user is not None and user.is_active:
        raw_token = secrets.token_urlsafe(32)
        token = PasswordResetToken(
            user_id=user.id,
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=_now() + timedelta(minutes=30),
        )
        db.session.add(token)
        db.session.commit()
        current_app.logger.info("Password reset requested for user_id=%s", user.id)
    return success(message=GENERIC_RESET_MESSAGE)


@auth_api.post("/reset-password")
def reset_password():
    body = request.get_json(silent=True) or {}
    raw_token = body.get("token")
    password = body.get("password")
    if not isinstance(raw_token, str) or not isinstance(password, str) or len(password) < 8:
        return failure("Validation failed", 422, {"password": ["Use at least 8 characters."]})
    token = db.session.scalar(
        db.select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hashlib.sha256(raw_token.encode()).hexdigest(),
            PasswordResetToken.used_at.is_(None),
        )
    )
    if token is None or _utc(token.expires_at) <= _now():
        return failure("Invalid or expired reset token", 400)
    user = db.session.get(User, token.user_id)
    if user is None or not user.is_active:
        return failure("Invalid or expired reset token", 400)
    user.password_hash = generate_password_hash(password)
    user.must_change_password = False
    token.used_at = _now()
    db.session.commit()
    return success(message="Password reset successful")
