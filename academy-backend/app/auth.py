from functools import wraps
from typing import Callable

from flask import g
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from .extensions import db
from .models import RevokedToken
from .responses import failure


def jwt_is_revoked(jwt_payload: dict) -> bool:
    return db.session.scalar(
        db.select(RevokedToken.id).where(RevokedToken.jti == jwt_payload.get("jti"))
    ) is not None


def roles_required(*roles: str):
    allowed = set(roles)

    def decorator(view: Callable):
        @wraps(view)
        def wrapped(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in allowed:
                return failure("Forbidden", 403)
            g.current_user_id = int(claims["sub"])
            g.current_claims = claims
            return view(*args, **kwargs)

        return wrapped

    return decorator


def authenticated(view: Callable):
    @wraps(view)
    def wrapped(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        g.current_user_id = int(claims["sub"])
        g.current_claims = claims
        return view(*args, **kwargs)

    return wrapped
