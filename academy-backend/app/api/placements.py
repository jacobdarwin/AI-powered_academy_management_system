from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps

from flask import Blueprint, Response, g, request
from sqlalchemy.exc import IntegrityError

from ..auth import authenticated
from ..extensions import db
from ..models import (
    Application, Assessment, Attendance, Certificate, Company, Course, Mark,
    PlacementDrive, Student,
)
from ..responses import failure, success

placements_api = Blueprint("placements", __name__)


def _placement_staff(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        from flask_jwt_extended import get_jwt, verify_jwt_in_request
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "superadmin" and not (
            claims.get("role") == "staff"
            and claims.get("designation") in {"placement_officer", "admin", "manager"}
        ):
            return failure("Forbidden", 403)
        g.current_user_id = int(claims["sub"])
        g.current_claims = claims
        return view(*args, **kwargs)
    return wrapped


def _date(value):
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _decimal(value):
    try:
        return Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        return None


def _company(item):
    return {"id": item.id, "name": item.name, "website": item.website, "contact": item.contact}


def _drive(item):
    return {
        "id": item.id, "company_id": item.company_id, "title": item.title,
        "role": item.role, "drive_date": item.drive_date.isoformat(),
        "package": str(item.package) if item.package is not None else None,
        "course_id": item.course_id,
        "attendance_threshold": str(item.attendance_threshold) if item.attendance_threshold is not None else None,
        "marks_threshold": str(item.marks_threshold) if item.marks_threshold is not None else None,
        "status": item.status,
    }


def _application(item):
    return {"id": item.id, "drive_id": item.drive_id, "student_id": item.student_id,
            "stage": item.stage, "offer_details": item.offer_details}


def _certificate(item):
    return {"id": item.id, "student_id": item.student_id, "certificate_no": item.certificate_no,
            "issued_on": item.issued_on.isoformat(), "file_path": item.file_path}


def _student_for_user():
    return db.session.scalar(db.select(Student).where(Student.user_id == g.current_user_id))


def _metrics(student_id):
    attendance = db.session.scalars(db.select(Attendance).where(Attendance.student_id == student_id)).all()
    sessions = [a for a in attendance if a.status != "leave"]
    attendance_pct = (sum(a.status in {"present", "late"} for a in sessions) / len(sessions) * 100) if sessions else 0
    marks = db.session.execute(
        db.select(Mark, Assessment).join(Assessment, Mark.assessment_id == Assessment.id)
        .where(Mark.student_id == student_id)
    ).all()
    maximum = sum(Decimal(str(a.max_marks)) for _, a in marks)
    obtained = sum(Decimal(str(m.marks_obtained)) for m, _ in marks)
    marks_pct = float(obtained / maximum * 100) if maximum else 0
    return round(attendance_pct, 2), round(marks_pct, 2)


@placements_api.route("/companies", methods=["GET", "POST"])
@_placement_staff
def companies():
    if request.method == "GET":
        return success([_company(x) for x in db.session.scalars(db.select(Company).order_by(Company.name))])
    body = request.get_json(silent=True) or {}
    name = str(body.get("name", "")).strip()
    if not name:
        return failure("Validation failed", 422, {"name": ["Name is required."]})
    item = Company(name=name, website=body.get("website"), contact=body.get("contact"))
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("Company already exists", 409)
    return success(_company(item), "Company created", 201)


@placements_api.route("/companies/<int:company_id>", methods=["GET", "PATCH"])
@_placement_staff
def company(company_id):
    item = db.session.get(Company, company_id)
    if not item:
        return failure("Company not found", 404)
    if request.method == "PATCH":
        body = request.get_json(silent=True) or {}
        for field in ("name", "website", "contact"):
            if field in body:
                setattr(item, field, body[field])
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return failure("Company already exists", 409)
    return success(_company(item))


@placements_api.route("/drives", methods=["GET", "POST"])
@_placement_staff
def drives():
    if request.method == "GET":
        statement = db.select(PlacementDrive).order_by(PlacementDrive.drive_date)
        if request.args.get("status"):
            statement = statement.where(PlacementDrive.status == request.args["status"])
        return success([_drive(x) for x in db.session.scalars(statement)])
    body = request.get_json(silent=True) or {}
    drive_date = _date(body.get("drive_date") or body.get("date"))
    company_id, title, role = body.get("company_id"), body.get("title"), body.get("role")
    if not isinstance(company_id, int) or not title or not role or not drive_date:
        return failure("Validation failed", 422, {"drive": ["Company, title, role, and date are required."]})
    if not db.session.get(Company, company_id):
        return failure("Company not found", 404)
    item = PlacementDrive(company_id=company_id, title=str(title).strip(), role=str(role).strip(),
        drive_date=drive_date, package=_decimal(body.get("package")),
        course_id=body.get("course_id"), attendance_threshold=_decimal(body.get("attendance_threshold")),
        marks_threshold=_decimal(body.get("marks_threshold")), status=body.get("status", "open"))
    db.session.add(item)
    db.session.commit()
    return success(_drive(item), "Drive created", 201)


@placements_api.route("/drives/<int:drive_id>", methods=["GET", "PATCH"])
@_placement_staff
def drive(drive_id):
    item = db.session.get(PlacementDrive, drive_id)
    if not item:
        return failure("Drive not found", 404)
    if request.method == "PATCH":
        body = request.get_json(silent=True) or {}
        for field in ("company_id", "title", "role", "course_id", "status"):
            if field in body:
                setattr(item, field, body[field])
        if "date" in body or "drive_date" in body:
            item.drive_date = _date(body.get("drive_date") or body.get("date"))
        for field in ("package", "attendance_threshold", "marks_threshold"):
            if field in body:
                setattr(item, field, _decimal(body[field]))
        db.session.commit()
    return success(_drive(item))


@placements_api.get("/placements/open")
@authenticated
def open_drives():
    student = _student_for_user()
    if not student:
        return failure("Student profile not found", 404)
    statement = db.select(PlacementDrive).where(PlacementDrive.status == "open")
    statement = statement.where((PlacementDrive.course_id.is_(None)) | (PlacementDrive.course_id == student.course_id))
    return success([_drive(x) for x in db.session.scalars(statement.order_by(PlacementDrive.drive_date))])


@placements_api.route("/applications", methods=["GET", "POST"])
@authenticated
def applications():
    claims = g.current_claims
    if request.method == "GET":
        if claims.get("role") == "student":
            student = _student_for_user()
            statement = db.select(Application).where(Application.student_id == student.id) if student else db.select(Application).where(Application.id == -1)
        elif claims.get("role") in {"superadmin", "staff"}:
            statement = db.select(Application)
        else:
            return failure("Forbidden", 403)
        return success([_application(x) for x in db.session.scalars(statement.order_by(Application.id.desc()))])
    if claims.get("role") != "student":
        return failure("Forbidden", 403)
    student = _student_for_user()
    drive = db.session.get(PlacementDrive, (request.get_json(silent=True) or {}).get("drive_id"))
    if not student or not drive:
        return failure("Student or drive not found", 404)
    if drive.status != "open":
        return failure("Drive is not open", 422)
    if drive.course_id is not None and drive.course_id != student.course_id:
        return failure("Student is not eligible for this course", 422)
    attendance, marks = _metrics(student.id)
    if drive.attendance_threshold is not None and attendance < float(drive.attendance_threshold):
        return failure("Attendance threshold not met", 422, {"attendance": attendance})
    if drive.marks_threshold is not None and marks < float(drive.marks_threshold):
        return failure("Marks threshold not met", 422, {"marks": marks})
    if db.session.scalar(db.select(Application.id).where(Application.drive_id == drive.id, Application.student_id == student.id)):
        return failure("Already applied to this drive", 409)
    item = Application(drive_id=drive.id, student_id=student.id)
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("Already applied to this drive", 409)
    return success(_application(item), "Application submitted", 201)


@placements_api.get("/me/applications")
@authenticated
def my_applications():
    student = _student_for_user()
    if not student:
        return failure("Student profile not found", 404)
    return success([_application(x) for x in db.session.scalars(db.select(Application).where(Application.student_id == student.id))])


@placements_api.patch("/applications/<int:application_id>")
@_placement_staff
def update_application(application_id):
    item = db.session.get(Application, application_id)
    if not item:
        return failure("Application not found", 404)
    body = request.get_json(silent=True) or {}
    if "status" in body or "stage" in body:
        item.stage = body.get("status", body.get("stage"))
        if item.stage in {"selected", "offered", "hired"}:
            student = db.session.get(Student, item.student_id)
            student.placed_status = "placed"
    if "offer_details" in body:
        item.offer_details = body["offer_details"]
    db.session.commit()
    return success(_application(item))


@placements_api.get("/certificates/eligibility")
@authenticated
def certificate_eligibility():
    student = _student_for_user() if g.current_claims.get("role") == "student" else db.session.get(Student, request.args.get("student_id", type=int))
    if not student:
        return failure("Student not found", 404)
    attendance, marks = _metrics(student.id)
    eligible = student.status == "active" and attendance >= 75 and marks >= 50
    return success({"student_id": student.id, "eligible": eligible, "attendance": attendance, "marks": marks,
                    "reasons": [] if eligible else ["Minimum attendance is 75% and marks are 50%."]})


@placements_api.get("/me/certificates")
@authenticated
def my_certificates():
    student = _student_for_user()
    if not student:
        return failure("Student profile not found", 404)
    return success([_certificate(x) for x in db.session.scalars(db.select(Certificate).where(Certificate.student_id == student.id))])


@placements_api.post("/certificates")
@_placement_staff
def issue_certificate():
    student = db.session.get(Student, (request.get_json(silent=True) or {}).get("student_id"))
    if not student:
        return failure("Student not found", 404)
    attendance, marks = _metrics(student.id)
    if student.status != "active" or attendance < 75 or marks < 50:
        return failure("Student is not eligible for a certificate", 422)
    existing = db.session.scalar(db.select(Certificate).where(Certificate.student_id == student.id))
    if existing:
        return success(_certificate(existing))
    item = Certificate(student_id=student.id, certificate_no=f"CERT-{student.id}-{date.today().strftime('%Y%m%d')}", issued_on=date.today())
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("Certificate already issued", 409)
    return success(_certificate(item), "Certificate issued", 201)


@placements_api.get("/certificates/<int:certificate_id>/download")
@authenticated
def download_certificate(certificate_id):
    item = db.session.get(Certificate, certificate_id)
    if not item:
        return failure("Certificate not found", 404)
    if g.current_claims.get("role") == "student":
        student = _student_for_user()
        if not student or student.id != item.student_id:
            return failure("Forbidden", 403)
    text = f"%PDF-1.4\nAcademy Certificate\nCertificate No: {item.certificate_no}\nStudent ID: {item.student_id}\nIssued: {item.issued_on}\n%%EOF"
    return Response(text.encode(), mimetype="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{item.certificate_no}.pdf"'})
