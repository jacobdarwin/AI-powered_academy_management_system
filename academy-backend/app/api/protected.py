from flask import Blueprint

from ..auth import roles_required
from ..responses import success

protected_api = Blueprint("protected", __name__, url_prefix="/protected")


@protected_api.get("/superadmin-check")
@roles_required("superadmin")
def superadmin_check():
    return success({"authorized": True})


@protected_api.get("/staff-check")
@roles_required("staff")
def staff_check():
    return success({"authorized": True})
