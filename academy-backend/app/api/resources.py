from datetime import date
from decimal import Decimal, InvalidOperation
import secrets
import csv
import io

from flask import Blueprint, g, request, current_app
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from ..auth import authenticated, roles_required
from ..extensions import db
from ..models import Batch, Course, Staff, Student, User
from ..responses import failure, success

resources_api = Blueprint("resources", __name__)


def _text(body: dict, key: str, required: bool = True) -> str | None:
    value = body.get(key)
    if value is None:
        return None if not required else ""
    return str(value).strip()


def _decimal(body: dict, key: str):
    try:
        value = Decimal(str(body[key]))
    except (KeyError, InvalidOperation, TypeError):
        return None
    return value


def _page(query):
    try:
        page = max(1, int(query.get("page", 1)))
        per_page = min(100, max(1, int(query.get("per_page", 20))))
    except (TypeError, ValueError):
        page, per_page = 1, 20
    return page, per_page


def _paged(statement, query, serializer):
    page, per_page = _page(query)
    result = db.paginate(statement, page=page, per_page=per_page, error_out=False)
    return success(
        [serializer(item) for item in result.items],
        meta={
            "page": page,
            "per_page": per_page,
            "total": result.total,
            "pages": result.pages,
        },
    )


def _user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "login_id": user.login_id,
        "role": user.role,
        "is_active": user.is_active,
        "must_change_password": user.must_change_password,
    }


def _course(course: Course) -> dict:
    return {
        "id": course.id,
        "name": course.name,
        "code": course.code,
        "duration_months": course.duration_months,
        "total_fee": str(course.total_fee),
        "description": course.description,
        "is_active": course.is_active,
    }


def _staff(staff: Staff) -> dict:
    return {
        "id": staff.id,
        "user_id": staff.user_id,
        "staff_code": staff.staff_code,
        "name": staff.name,
        "phone": staff.phone,
        "designation": staff.designation,
        "qualification": staff.qualification,
        "joined_on": staff.joined_on.isoformat() if staff.joined_on else None,
        "status": staff.status,
    }


def _batch(batch: Batch) -> dict:
    return {
        "id": batch.id,
        "code": batch.code,
        "course_id": batch.course_id,
        "trainer_id": batch.trainer_id,
        "schedule": batch.schedule,
        "start_date": batch.start_date.isoformat() if batch.start_date else None,
        "end_date": batch.end_date.isoformat() if batch.end_date else None,
        "capacity": batch.capacity,
        "status": batch.status,
    }


def _student(student: Student) -> dict:
    return {
        "id": student.id,
        "user_id": student.user_id,
        "student_code": student.student_code,
        "name": student.name,
        "email": student.email,
        "phone": student.phone,
        "course_id": student.course_id,
        "batch_id": student.batch_id,
        "admission_date": (
            student.admission_date.isoformat() if student.admission_date else None
        ),
        "status": student.status,
        "placed_status": student.placed_status,
    }


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


@resources_api.get("/users")
@roles_required("superadmin")
def list_users():
    query = request.args
    statement = db.select(User).order_by(User.id.desc())
    if query.get("q"):
        term = f"%{query['q'].strip()}%"
        statement = statement.where(or_(User.email.ilike(term), User.login_id.ilike(term)))
    if query.get("role"):
        statement = statement.where(User.role == query["role"].strip().lower())
    return _paged(statement, query, _user)


@resources_api.post("/users")
@roles_required("superadmin")
def create_user():
    body = request.get_json(silent=True) or {}
    login_id = _text(body, "login_id", required=False) or _text(body, "email", required=False)
    password = body.get("password")
    role = _text(body, "role")
    if not login_id or not isinstance(password, str) or len(password) < 8:
        return failure("Validation failed", 422, {"login_id": ["Email or login ID is required."], "password": ["Use at least 8 characters."]})
    if role not in {"superadmin", "staff", "student"}:
        return failure("Validation failed", 422, {"role": ["Unsupported role."]})
    user = User(
        email=_text(body, "email", required=False) or None,
        login_id=login_id,
        password_hash=generate_password_hash(password),
        role=role,
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("A user with that login ID or email already exists", 409)
    return success(_user(user), "User created", 201)


@resources_api.get("/users/<int:user_id>")
@roles_required("superadmin")
def get_user(user_id: int):
    user = db.session.get(User, user_id)
    return success(_user(user)) if user else failure("User not found", 404)


@resources_api.patch("/users/<int:user_id>")
@roles_required("superadmin")
def update_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return failure("User not found", 404)
    body = request.get_json(silent=True) or {}
    for field in ("email", "login_id"):
        if field in body and isinstance(body[field], str) and body[field].strip():
            setattr(user, field, body[field].strip())
    if "is_active" in body and isinstance(body["is_active"], bool):
        user.is_active = body["is_active"]
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("A user with that login ID or email already exists", 409)
    return success(_user(user))


@resources_api.post("/users/<int:user_id>/activate")
@roles_required("superadmin")
def activate_user(user_id: int):
    return _set_user_active(user_id, True)


@resources_api.post("/users/<int:user_id>/deactivate")
@roles_required("superadmin")
def deactivate_user(user_id: int):
    return _set_user_active(user_id, False)


@resources_api.post("/users/<int:user_id>/reset-password")
@roles_required("superadmin")
def reset_user_password(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return failure("User not found", 404)
    body = request.get_json(silent=True) or {}
    password = str(body.get("password", "")).strip() or secrets.token_urlsafe(9)
    if len(password) < 8:
        return failure("Validation failed", 422, {"password": ["Use at least 8 characters."]})
    user.password_hash = generate_password_hash(password)
    user.must_change_password = True
    db.session.commit()
    return success({"temporary_password": password}, "Password reset")


def _set_user_active(user_id: int, is_active: bool):
    user = db.session.get(User, user_id)
    if not user:
        return failure("User not found", 404)
    user.is_active = is_active
    db.session.commit()
    return success(_user(user))


@resources_api.get("/courses")
@authenticated
def list_courses():
    query = request.args
    statement = db.select(Course).where(Course.is_deleted.is_(False)).order_by(Course.name)
    if query.get("q"):
        term = f"%{query['q'].strip()}%"
        statement = statement.where(or_(Course.name.ilike(term), Course.code.ilike(term)))
    return _paged(statement, query, _course)


@resources_api.post("/courses")
@roles_required("superadmin")
def create_course():
    body = request.get_json(silent=True) or {}
    name, code = _text(body, "name"), _text(body, "code")
    duration, total_fee = body.get("duration_months"), _decimal(body, "total_fee")
    if not name or not code or not isinstance(duration, int) or duration <= 0 or total_fee is None:
        return failure("Validation failed", 422, {"course": ["Name, code, duration, and fee are required."]})
    course = Course(
        name=name,
        code=code.upper(),
        duration_months=duration,
        total_fee=total_fee,
        description=_text(body, "description", required=False),
    )
    db.session.add(course)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("Course code already exists", 409)
    return success(_course(course), "Course created", 201)


@resources_api.patch("/courses/<int:course_id>")
@roles_required("superadmin")
def update_course(course_id: int):
    course = db.session.get(Course, course_id)
    if not course or course.is_deleted:
        return failure("Course not found", 404)
    body = request.get_json(silent=True) or {}
    if "name" in body and _text(body, "name"):
        course.name = _text(body, "name")
    if "description" in body:
        course.description = _text(body, "description", required=False)
    if "duration_months" in body and isinstance(body["duration_months"], int):
        course.duration_months = body["duration_months"]
    if "total_fee" in body:
        total_fee = _decimal(body, "total_fee")
        if total_fee is None:
            return failure("Validation failed", 422, {"total_fee": ["Enter a valid amount."]})
        course.total_fee = total_fee
    if "is_active" in body and isinstance(body["is_active"], bool):
        course.is_active = body["is_active"]
    db.session.commit()
    return success(_course(course))


@resources_api.delete("/courses/<int:course_id>")
@roles_required("superadmin")
def delete_course(course_id: int):
    course = db.session.get(Course, course_id)
    if not course or course.is_deleted:
        return failure("Course not found", 404)
    course.is_deleted = True
    course.is_active = False
    db.session.commit()
    return success(message="Course archived")


@resources_api.get("/staff")
@roles_required("superadmin")
def list_staff():
    query = request.args
    statement = db.select(Staff).where(Staff.is_deleted.is_(False)).order_by(Staff.name)
    if query.get("q"):
        statement = statement.where(Staff.name.ilike(f"%{query['q'].strip()}%"))
    if query.get("designation"):
        statement = statement.where(Staff.designation == query["designation"])
    return _paged(statement, query, _staff)


@resources_api.get("/staff/workload")
@roles_required("superadmin")
def staff_workload():
    staff = db.session.scalars(
        db.select(Staff).where(Staff.is_deleted.is_(False)).order_by(Staff.name)
    ).all()
    return success([{
        **_staff(item),
        "active_batches": 0,
        "batch_count": 0,
    } for item in staff])


@resources_api.post("/staff")
@roles_required("superadmin")
def create_staff():
    body = request.get_json(silent=True) or {}
    name, designation, staff_code = (
        _text(body, "name"),
        _text(body, "designation"),
        _text(body, "staff_code"),
    )
    user_id = body.get("user_id")
    if not name or not designation or not staff_code or not isinstance(user_id, int):
        return failure("Validation failed", 422, {"staff": ["Name, code, designation, and user_id are required."]})
    user = db.session.get(User, user_id)
    if not user or user.role != "staff":
        return failure("A staff user account is required", 422)
    staff = Staff(
        user_id=user_id,
        name=name,
        designation=designation,
        staff_code=staff_code.upper(),
        phone=_text(body, "phone", required=False),
        qualification=_text(body, "qualification", required=False),
        joined_on=_parse_date(body.get("joined_on")),
    )
    db.session.add(staff)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("Staff code or account is already assigned", 409)
    return success(_staff(staff), "Staff created", 201)


@resources_api.patch("/staff/<int:staff_id>")
@roles_required("superadmin")
def update_staff(staff_id: int):
    staff = db.session.get(Staff, staff_id)
    if not staff or staff.is_deleted:
        return failure("Staff not found", 404)
    body = request.get_json(silent=True) or {}
    for field in ("name", "phone", "designation", "qualification", "status"):
        if field in body and isinstance(body[field], str) and body[field].strip():
            setattr(staff, field, body[field].strip())
    if "joined_on" in body:
        staff.joined_on = _parse_date(body.get("joined_on"))
    db.session.commit()
    return success(_staff(staff))


@resources_api.delete("/staff/<int:staff_id>")
@roles_required("superadmin")
def delete_staff(staff_id: int):
    staff = db.session.get(Staff, staff_id)
    if not staff or staff.is_deleted:
        return failure("Staff not found", 404)
    staff.is_deleted = True
    staff.status = "inactive"
    db.session.commit()
    return success(message="Staff archived")


@resources_api.get("/batches")
@authenticated
def list_batches():
    query = request.args
    statement = db.select(Batch).order_by(Batch.start_date.desc(), Batch.id.desc())
    if query.get("course_id"):
        statement = statement.where(Batch.course_id == query["course_id"])
    if query.get("trainer_id"):
        statement = statement.where(Batch.trainer_id == query["trainer_id"])
    return _paged(statement, query, _batch)


@resources_api.post("/batches")
@roles_required("superadmin")
def create_batch():
    body = request.get_json(silent=True) or {}
    code = _text(body, "code")
    course_id, capacity = body.get("course_id"), body.get("capacity")
    if not code or not isinstance(course_id, int) or not isinstance(capacity, int) or capacity <= 0:
        return failure("Validation failed", 422, {"batch": ["Code, course_id, and positive capacity are required."]})
    if not db.session.get(Course, course_id):
        return failure("Course not found", 404)
    batch = Batch(
        code=code.upper(),
        course_id=course_id,
        trainer_id=body.get("trainer_id"),
        schedule=_text(body, "schedule", required=False),
        start_date=_parse_date(body.get("start_date")),
        end_date=_parse_date(body.get("end_date")),
        capacity=capacity,
    )
    db.session.add(batch)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("Batch code already exists", 409)
    return success(_batch(batch), "Batch created", 201)


@resources_api.patch("/batches/<int:batch_id>")
@roles_required("superadmin")
def update_batch(batch_id: int):
    batch = db.session.get(Batch, batch_id)
    if not batch:
        return failure("Batch not found", 404)
    body = request.get_json(silent=True) or {}
    for field in ("schedule", "status"):
        if field in body and isinstance(body[field], str):
            setattr(batch, field, body[field].strip())
    for field in ("start_date", "end_date"):
        if field in body:
            parsed = _parse_date(body.get(field))
            if body[field] and parsed is None:
                return failure("Validation failed", 422, {field: ["Use YYYY-MM-DD."]})
            setattr(batch, field, parsed)
    if "capacity" in body and isinstance(body["capacity"], int) and body["capacity"] > 0:
        batch.capacity = body["capacity"]
    if "trainer_id" in body:
        batch.trainer_id = body["trainer_id"]
    db.session.commit()
    return success(_batch(batch))


@resources_api.delete("/batches/<int:batch_id>")
@roles_required("superadmin")
def delete_batch(batch_id: int):
    batch = db.session.get(Batch, batch_id)
    if not batch:
        return failure("Batch not found", 404)
    batch.status = "archived"
    db.session.commit()
    return success(message="Batch archived")


@resources_api.get("/students")
@authenticated
def list_students():
    query = request.args
    statement = db.select(Student).where(Student.is_deleted.is_(False)).order_by(Student.name)
    if g.current_claims.get("role") == "student":
        statement = statement.where(Student.user_id == g.current_user_id)
    if query.get("q"):
        term = f"%{query['q'].strip()}%"
        statement = statement.where(
            or_(Student.name.ilike(term), Student.student_code.ilike(term), Student.email.ilike(term))
        )
    if query.get("status"):
        statement = statement.where(Student.status == query["status"])
    if query.get("course_id"):
        statement = statement.where(Student.course_id == query["course_id"])
    return _paged(statement, query, _student)


@resources_api.get("/students/export")
@roles_required("superadmin", "staff")
def export_students():
    students = db.session.scalars(
        db.select(Student).where(Student.is_deleted.is_(False)).order_by(Student.name)
    ).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["student_code", "name", "email", "phone", "status"])
    writer.writerows([[item.student_code, item.name, item.email or "", item.phone or "", item.status] for item in students])
    return current_app.response_class(
        output.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students.csv"},
    )


@resources_api.get("/students/<int:student_id>")
@authenticated
def get_student(student_id: int):
    student = db.session.get(Student, student_id)
    if not student or student.is_deleted:
        return failure("Student not found", 404)
    if g.current_claims.get("role") == "student" and student.user_id != g.current_user_id:
        return failure("Forbidden", 403)
    return success(_student(student))


@resources_api.post("/students")
@roles_required("superadmin", "staff")
def create_student():
    body = request.get_json(silent=True) or {}
    name, code, user_id = _text(body, "name"), _text(body, "student_code"), body.get("user_id")
    if not name or not code or not isinstance(user_id, int):
        return failure("Validation failed", 422, {"student": ["Name, student_code, and user_id are required."]})
    user = db.session.get(User, user_id)
    if not user or user.role != "student":
        return failure("A student user account is required", 422)
    student = Student(
        user_id=user_id,
        student_code=code.upper(),
        name=name,
        email=_text(body, "email", required=False),
        phone=_text(body, "phone", required=False),
        course_id=body.get("course_id"),
        batch_id=body.get("batch_id"),
        admission_date=_parse_date(body.get("admission_date")),
        guardian_name=_text(body, "guardian_name", required=False),
        address=_text(body, "address", required=False),
    )
    db.session.add(student)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("Student code or account is already assigned", 409)
    return success(_student(student), "Student created", 201)


@resources_api.patch("/students/<int:student_id>")
@authenticated
def update_student(student_id: int):
    student = db.session.get(Student, student_id)
    if not student or student.is_deleted:
        return failure("Student not found", 404)
    role = g.current_claims.get("role")
    if role == "student":
        if student.user_id != g.current_user_id:
            return failure("Forbidden", 403)
        allowed = {"phone", "email", "guardian_name", "guardian_phone", "address"}
    elif role not in {"superadmin", "staff"}:
        return failure("Forbidden", 403)
    else:
        allowed = {
            "name", "email", "phone", "guardian_name", "guardian_phone",
            "address", "status", "course_id", "batch_id",
        }
    body = request.get_json(silent=True) or {}
    for field in allowed:
        if field in body:
            setattr(student, field, body[field])
    db.session.commit()
    return success(_student(student))
