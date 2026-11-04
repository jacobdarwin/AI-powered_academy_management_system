from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, g, request
from sqlalchemy import func

from ..auth import authenticated, roles_required
from ..extensions import db
from ..models import (
    Assessment,
    Attendance,
    Batch,
    Mark,
    Setting,
    Staff,
    Student,
)
from ..responses import failure, success

academics_api = Blueprint("academics", __name__)

ATTENDANCE_STATUSES = {"present", "late", "absent", "leave"}


def _date(value):
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _staff_id():
    return db.session.scalar(db.select(Staff.id).where(Staff.user_id == g.current_user_id))


def _batch_allowed(batch_id: int) -> bool:
    claims = g.current_claims
    if claims.get("role") == "superadmin":
        return True
    return (
        claims.get("role") == "staff"
        and claims.get("designation") == "trainer"
        and db.session.scalar(
            db.select(Batch.id).where(
                Batch.id == batch_id, Batch.trainer_id == _staff_id()
            )
        )
        is not None
    )


def _attendance(item: Attendance) -> dict:
    return {
        "id": item.id,
        "student_id": item.student_id,
        "batch_id": item.batch_id,
        "date": item.date.isoformat(),
        "status": item.status,
        "note": item.note,
    }


def _assessment(item: Assessment) -> dict:
    return {
        "id": item.id,
        "batch_id": item.batch_id,
        "title": item.title,
        "assessment_type": item.assessment_type,
        "max_marks": str(item.max_marks),
        "date": item.date.isoformat(),
    }


def _mark(item: Mark) -> dict:
    return {
        "id": item.id,
        "assessment_id": item.assessment_id,
        "student_id": item.student_id,
        "marks_obtained": str(item.marks_obtained),
        "feedback": item.feedback,
    }


def _attendance_percentage(records: list[Attendance]) -> float:
    included = [item for item in records if item.status != "leave"]
    if not included:
        return 0.0
    setting = db.session.scalar(
        db.select(Setting).where(Setting.key == "attendance_late_weight")
    )
    late_weight = Decimal("1")
    if setting and isinstance(setting.value, (int, float, str)):
        try:
            late_weight = Decimal(str(setting.value))
        except InvalidOperation:
            pass
    score = sum(
        Decimal("1") if item.status == "present" else
        late_weight if item.status == "late" else Decimal("0")
        for item in included
    )
    return round(float(score / Decimal(len(included)) * 100), 2)


def _summary(student_id: int, from_date=None, to_date=None) -> dict:
    statement = db.select(Attendance).where(Attendance.student_id == student_id)
    if from_date:
        statement = statement.where(Attendance.date >= from_date)
    if to_date:
        statement = statement.where(Attendance.date <= to_date)
    records = list(db.session.scalars(statement.order_by(Attendance.date)))
    counts = {status: sum(item.status == status for item in records) for status in ATTENDANCE_STATUSES}
    return {
        "student_id": student_id,
        "percentage": _attendance_percentage(records),
        "total_sessions": len([item for item in records if item.status != "leave"]),
        "counts": counts,
        "records": [_attendance(item) for item in records],
    }


@academics_api.post("/attendance/bulk")
@roles_required("superadmin", "staff")
def bulk_attendance():
    body = request.get_json(silent=True) or {}
    batch_id = body.get("batch_id")
    attendance_date = _date(body.get("date"))
    records = body.get("records")
    if not isinstance(batch_id, int) or attendance_date is None or not isinstance(records, list):
        return failure("Validation failed", 422, {"attendance": ["Batch, date, and records are required."]})
    if attendance_date > date.today():
        return failure("Cannot mark attendance for a future date", 422)
    if not _batch_allowed(batch_id):
        return failure("Forbidden", 403)
    student_ids = {item.get("student_id") for item in records if isinstance(item, dict)}
    students = db.session.scalars(
        db.select(Student).where(Student.id.in_(student_ids), Student.batch_id == batch_id)
    ).all()
    if len(students) != len(student_ids):
        return failure("All students must belong to the selected batch", 422)
    for item in records:
        status = item.get("status")
        if status not in ATTENDANCE_STATUSES:
            return failure("Validation failed", 422, {"status": ["Unsupported attendance status."]})
        existing = db.session.scalar(
            db.select(Attendance).where(
                Attendance.student_id == item["student_id"],
                Attendance.date == attendance_date,
            )
        )
        if existing:
            existing.status = status
            existing.note = item.get("note")
        else:
            db.session.add(
                Attendance(
                    student_id=item["student_id"],
                    batch_id=batch_id,
                    date=attendance_date,
                    status=status,
                    note=item.get("note"),
                )
            )
    db.session.commit()
    return success({"saved": len(records)}, "Attendance saved")


@academics_api.get("/attendance")
@roles_required("superadmin", "staff")
def list_attendance():
    batch_id = request.args.get("batch_id", type=int)
    attendance_date = _date(request.args.get("date"))
    if not batch_id or not _batch_allowed(batch_id):
        return failure("Forbidden", 403)
    statement = db.select(Attendance).where(Attendance.batch_id == batch_id)
    if attendance_date:
        statement = statement.where(Attendance.date == attendance_date)
    records = list(db.session.scalars(statement.order_by(Attendance.date, Attendance.student_id)))
    return success([_attendance(item) for item in records])


@academics_api.get("/students/<int:student_id>/attendance")
@authenticated
def student_attendance(student_id: int):
    student = db.session.get(Student, student_id)
    if not student:
        return failure("Student not found", 404)
    if g.current_claims.get("role") == "student" and student.user_id != g.current_user_id:
        return failure("Forbidden", 403)
    if g.current_claims.get("role") == "staff" and not _batch_allowed(student.batch_id):
        return failure("Forbidden", 403)
    from_date = _date(request.args.get("from"))
    to_date = _date(request.args.get("to"))
    return success(_summary(student_id, from_date, to_date))


@academics_api.get("/attendance/monthly-summary")
@roles_required("superadmin", "staff")
def monthly_summary():
    batch_id = request.args.get("batch_id", type=int)
    month = request.args.get("month", "")
    if not batch_id or not _batch_allowed(batch_id) or len(month) != 7:
        return failure("Validation failed", 422, {"month": ["Use YYYY-MM."]})
    try:
        start = date.fromisoformat(f"{month}-01")
    except ValueError:
        return failure("Validation failed", 422, {"month": ["Use YYYY-MM."]})
    end = date(start.year + (start.month == 12), 1 if start.month == 12 else start.month + 1, 1)
    students = db.session.scalars(db.select(Student).where(Student.batch_id == batch_id)).all()
    return success(
        [
            {
                "student_id": student.id,
                "percentage": _summary(student.id, start, end).get("percentage"),
            }
            for student in students
        ]
    )


@academics_api.post("/assessments")
@roles_required("superadmin", "staff")
def create_assessment():
    body = request.get_json(silent=True) or {}
    batch_id = body.get("batch_id")
    max_marks = body.get("max_marks")
    assessment_date = _date(body.get("date"))
    try:
        max_marks = Decimal(str(max_marks))
    except (InvalidOperation, TypeError):
        max_marks = Decimal("0")
    if (
        not isinstance(batch_id, int)
        or not _batch_allowed(batch_id)
        or not str(body.get("title", "")).strip()
        or max_marks <= 0
        or assessment_date is None
    ):
        return failure("Validation failed", 422, {"assessment": ["Valid batch, title, date, and max_marks are required."]})
    assessment = Assessment(
        batch_id=batch_id,
        title=str(body["title"]).strip(),
        assessment_type=str(body.get("assessment_type", "test")).strip(),
        max_marks=max_marks,
        date=assessment_date,
    )
    db.session.add(assessment)
    db.session.commit()
    return success(_assessment(assessment), "Assessment created", 201)


@academics_api.post("/marks/bulk")
@roles_required("superadmin", "staff")
def bulk_marks():
    body = request.get_json(silent=True) or {}
    assessment = db.session.get(Assessment, body.get("assessment_id"))
    records = body.get("records")
    if not assessment or not _batch_allowed(assessment.batch_id) or not isinstance(records, list):
        return failure("Forbidden", 403)
    student_ids = {item.get("student_id") for item in records if isinstance(item, dict)}
    valid_ids = set(
        db.session.scalars(
            db.select(Student.id).where(
                Student.id.in_(student_ids), Student.batch_id == assessment.batch_id
            )
        ).all()
    )
    if valid_ids != student_ids:
        return failure("All students must belong to the assessment batch", 422)
    for item in records:
        try:
            marks = Decimal(str(item.get("marks")))
        except (InvalidOperation, TypeError):
            return failure("Validation failed", 422, {"marks": ["Enter a valid mark."]})
        if marks < 0 or marks > assessment.max_marks:
            return failure("Marks cannot exceed the assessment maximum", 422)
        existing = db.session.scalar(
            db.select(Mark).where(
                Mark.assessment_id == assessment.id, Mark.student_id == item["student_id"]
            )
        )
        if existing:
            existing.marks_obtained = marks
            existing.feedback = item.get("feedback")
        else:
            db.session.add(
                Mark(
                    assessment_id=assessment.id,
                    student_id=item["student_id"],
                    marks_obtained=marks,
                    feedback=item.get("feedback"),
                )
            )
    db.session.commit()
    return success({"saved": len(records)}, "Marks saved")


@academics_api.get("/marks")
@authenticated
def list_marks():
    student_id = request.args.get("student_id", type=int)
    if g.current_claims.get("role") == "student":
        student = db.session.scalar(db.select(Student).where(Student.user_id == g.current_user_id))
        student_id = student.id if student else None
    statement = db.select(Mark).join(Assessment, Mark.assessment_id == Assessment.id)
    if g.current_claims.get("role") == "staff":
        if g.current_claims.get("designation") != "trainer":
            return failure("Forbidden", 403)
        statement = statement.join(Batch, Assessment.batch_id == Batch.id).where(
            Batch.trainer_id == _staff_id()
        )
    if student_id:
        statement = statement.where(Mark.student_id == student_id)
    records = list(db.session.scalars(statement.order_by(Mark.id.desc())))
    return success([_mark(item) for item in records])


@academics_api.get("/me/marks")
@roles_required("student")
def my_marks():
    student = db.session.scalar(db.select(Student).where(Student.user_id == g.current_user_id))
    if not student:
        return failure("Student profile not found", 404)
    records = list(db.session.scalars(db.select(Mark).where(Mark.student_id == student.id)))
    return success([_mark(item) for item in records])


@academics_api.get("/me/assessments")
@roles_required("student")
def my_assessments():
    student = db.session.scalar(db.select(Student).where(Student.user_id == g.current_user_id))
    if not student:
        return failure("Student profile not found", 404)
    assessments = db.session.scalars(
        db.select(Assessment).where(Assessment.batch_id == student.batch_id)
    ).all()
    return success([_assessment(item) for item in assessments])
