from datetime import date
import secrets
import string

from flask import Blueprint, g, request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from ..auth import roles_required
from ..extensions import db
from ..models import Lead, LeadFollowUp, Staff, Student, User
from ..responses import failure, success

leads_api = Blueprint("leads", __name__, url_prefix="/leads")


def _date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _lead(lead: Lead) -> dict:
    return {
        "id": lead.id,
        "name": lead.name,
        "phone": lead.phone,
        "email": lead.email,
        "course_id": lead.course_id,
        "source": lead.source,
        "counselor_id": lead.counselor_id,
        "follow_up_on": lead.follow_up_on.isoformat() if lead.follow_up_on else None,
        "note": lead.note,
        "status": lead.status,
        "converted_student_id": lead.converted_student_id,
    }


def _follow_up(item: LeadFollowUp) -> dict:
    return {
        "id": item.id,
        "lead_id": item.lead_id,
        "staff_id": item.staff_id,
        "follow_up_on": item.follow_up_on.isoformat(),
        "note": item.note,
        "status": item.status,
    }


def _page(query):
    try:
        page = max(1, int(query.get("page", 1)))
        per_page = min(100, max(1, int(query.get("per_page", 20))))
    except (TypeError, ValueError):
        page, per_page = 1, 20
    return page, per_page


def _allowed_counselor(lead: Lead) -> bool:
    claims = g.current_claims
    return claims.get("role") == "superadmin" or (
        claims.get("role") == "staff"
        and claims.get("designation") == "counselor"
        and lead.counselor_id
        == db.session.scalar(db.select(Staff.id).where(Staff.user_id == g.current_user_id))
    )


@leads_api.get("")
@roles_required("superadmin", "staff")
def list_leads():
    query = request.args
    statement = db.select(Lead).where(Lead.is_deleted.is_(False)).order_by(Lead.created_at.desc())
    if g.current_claims.get("role") == "staff":
        if g.current_claims.get("designation") != "counselor":
            return failure("Forbidden", 403)
        staff_id = db.session.scalar(
            db.select(Staff.id).where(Staff.user_id == g.current_user_id)
        )
        statement = statement.where(Lead.counselor_id == staff_id)
    if query.get("q"):
        term = f"%{query['q'].strip()}%"
        statement = statement.where(
            or_(Lead.name.ilike(term), Lead.phone.ilike(term), Lead.email.ilike(term))
        )
    if query.get("source"):
        statement = statement.where(Lead.source == query["source"])
    if query.get("status"):
        statement = statement.where(Lead.status == query["status"])
    page, per_page = _page(query)
    result = db.paginate(statement, page=page, per_page=per_page, error_out=False)
    return success(
        [_lead(item) for item in result.items],
        meta={"page": page, "per_page": per_page, "total": result.total, "pages": result.pages},
    )


@leads_api.post("")
@roles_required("superadmin", "staff")
def create_lead():
    body = request.get_json(silent=True) or {}
    if g.current_claims.get("role") == "staff" and g.current_claims.get("designation") != "counselor":
        return failure("Forbidden", 403)
    name = str(body.get("name", "")).strip()
    phone = str(body.get("phone", "")).strip()
    if not name or not phone:
        return failure("Validation failed", 422, {"lead": ["Name and phone are required."]})
    follow_up = _date(body.get("follow_up_on"))
    if body.get("follow_up_on") and follow_up is None:
        return failure("Validation failed", 422, {"follow_up_on": ["Use YYYY-MM-DD."]})
    counselor_id = body.get("counselor_id")
    if g.current_claims.get("role") == "staff":
        counselor_id = db.session.scalar(
            db.select(Staff.id).where(Staff.user_id == g.current_user_id)
        )
    lead = Lead(
        name=name,
        phone=phone,
        email=str(body.get("email", "")).strip() or None,
        course_id=body.get("course_id"),
        source=str(body.get("source", "")).strip() or None,
        counselor_id=counselor_id,
        follow_up_on=follow_up,
        note=str(body.get("note", "")).strip() or None,
        status=str(body.get("status", "new")).strip(),
    )
    db.session.add(lead)
    db.session.commit()
    return success(_lead(lead), "Lead created", 201)


@leads_api.get("/<int:lead_id>")
@roles_required("superadmin", "staff")
def get_lead(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead or lead.is_deleted:
        return failure("Lead not found", 404)
    if not _allowed_counselor(lead):
        return failure("Forbidden", 403)
    return success(_lead(lead))


@leads_api.patch("/<int:lead_id>")
@roles_required("superadmin", "staff")
def update_lead(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead or lead.is_deleted:
        return failure("Lead not found", 404)
    if not _allowed_counselor(lead):
        return failure("Forbidden", 403)
    body = request.get_json(silent=True) or {}
    for field in ("name", "phone", "email", "source", "note"):
        if field in body:
            setattr(lead, field, str(body[field]).strip() or None)
    if "follow_up_on" in body:
        parsed = _date(body["follow_up_on"])
        if body["follow_up_on"] and parsed is None:
            return failure("Validation failed", 422, {"follow_up_on": ["Use YYYY-MM-DD."]})
        lead.follow_up_on = parsed
    if "course_id" in body:
        lead.course_id = body["course_id"]
    db.session.commit()
    return success(_lead(lead))


@leads_api.patch("/<int:lead_id>/status")
@roles_required("superadmin", "staff")
def update_status(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead or lead.is_deleted:
        return failure("Lead not found", 404)
    if not _allowed_counselor(lead):
        return failure("Forbidden", 403)
    status = str((request.get_json(silent=True) or {}).get("status", "")).strip()
    if status not in {"new", "contacted", "follow_up", "interested", "enrolled", "lost"}:
        return failure("Validation failed", 422, {"status": ["Unsupported lead status."]})
    lead.status = status
    db.session.commit()
    return success(_lead(lead))


@leads_api.post("/<int:lead_id>/follow-ups")
@roles_required("superadmin", "staff")
def add_follow_up(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead or lead.is_deleted:
        return failure("Lead not found", 404)
    if not _allowed_counselor(lead):
        return failure("Forbidden", 403)
    body = request.get_json(silent=True) or {}
    follow_up_on = _date(body.get("follow_up_on"))
    note = str(body.get("note", "")).strip()
    if follow_up_on is None or not note:
        return failure("Validation failed", 422, {"follow_up": ["Date and note are required."]})
    item = LeadFollowUp(
        lead_id=lead.id,
        staff_id=g.current_user_id,
        follow_up_on=follow_up_on,
        note=note,
    )
    lead.follow_up_on = follow_up_on
    lead.status = "follow_up"
    db.session.add(item)
    db.session.commit()
    return success(_follow_up(item), "Follow-up added", 201)


@leads_api.post("/<int:lead_id>/convert")
@roles_required("superadmin", "staff")
def convert_lead(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead or lead.is_deleted:
        return failure("Lead not found", 404)
    if not _allowed_counselor(lead):
        return failure("Forbidden", 403)
    if lead.converted_student_id is not None or lead.status == "enrolled":
        return failure("Lead has already been converted", 409)
    body = request.get_json(silent=True) or {}
    student_code = str(body.get("student_code", "")).strip().upper()
    if not student_code:
        return failure("Validation failed", 422, {"student_code": ["Student code is required."]})
    if db.session.scalar(db.select(Student).where(Student.student_code == student_code)):
        return failure("Student code already exists", 409)
    temporary_password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    login_id = student_code
    if db.session.scalar(db.select(User).where(User.login_id == login_id)):
        return failure("Student login ID already exists", 409)
    user = User(
        email=lead.email,
        login_id=login_id,
        password_hash=generate_password_hash(temporary_password),
        role="student",
        must_change_password=True,
    )
    student = Student(
        user_id=None,
        student_code=student_code,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        course_id=lead.course_id,
        batch_id=body.get("batch_id"),
        admission_date=date.today(),
        lead_id=lead.id,
    )
    try:
        db.session.add(user)
        db.session.flush()
        student.user_id = user.id
        db.session.add(student)
        db.session.flush()
        lead.converted_student_id = student.id
        lead.status = "enrolled"
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("Lead conversion could not be completed", 409)
    return success(
        {
            "lead": _lead(lead),
            "student": {
                "id": student.id,
                "student_code": student.student_code,
                "user_id": user.id,
            },
            "temporary_password": temporary_password,
        },
        "Lead converted",
        201,
    )
