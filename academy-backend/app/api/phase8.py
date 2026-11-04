import csv
import io
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from flask import Blueprint, current_app, g, request, send_file
from sqlalchemy import func
from werkzeug.utils import secure_filename

from ..auth import authenticated, roles_required
from ..extensions import db
from ..models import (
    Application, Attendance, Batch, Company, Course, Expense, FeePlan, Installment,
    Lead, Material, Notification, NotificationRead, Payment, PlacementDrive,
    Setting, Staff, Student, User,
)
from ..responses import failure, success

phase8_api = Blueprint("phase8", __name__)
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "png", "jpg", "jpeg"}


def _date(value):
    try:
        return date.fromisoformat(str(value)) if value else None
    except (TypeError, ValueError):
        return None


def _student():
    return db.session.scalar(db.select(Student).where(Student.user_id == g.current_user_id))


def _batch_allowed(batch_id):
    if g.current_claims.get("role") == "superadmin":
        return True
    if g.current_claims.get("role") != "staff":
        student = _student()
        return student is not None and student.batch_id == batch_id
    staff_id = db.session.scalar(db.select(Staff.id).where(Staff.user_id == g.current_user_id))
    return db.session.scalar(db.select(Batch.id).where(Batch.id == batch_id, Batch.trainer_id == staff_id)) is not None


def _material(item):
    return {"id": item.id, "batch_id": item.batch_id, "title": item.title,
            "material_type": item.material_type, "file_size": item.file_size,
            "created_at": item.created_at.isoformat() if item.created_at else None}


@phase8_api.post("/materials")
@phase8_api.post("/materials/upload")
@roles_required("superadmin", "staff")
def upload_material():
    batch_id = request.form.get("batch_id", type=int)
    title = request.form.get("title", "").strip()
    material_type = request.form.get("material_type", "document").strip().lower()
    uploaded = request.files.get("file")
    if not batch_id or not title or not uploaded or not uploaded.filename or not _batch_allowed(batch_id):
        return failure("Batch, title, file, and permission are required", 422)
    filename = secure_filename(uploaded.filename)
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if not filename or extension not in ALLOWED_EXTENSIONS:
        return failure("Unsupported file type", 422)
    data = uploaded.read()
    if not data or len(data) > current_app.config["MATERIAL_MAX_BYTES"]:
        return failure("File is empty or too large", 422)
    folder = Path(current_app.config["UPLOAD_DIR"]) / "materials"
    folder.mkdir(parents=True, exist_ok=True)
    stored = f"{uuid.uuid4().hex}.{extension}"
    path = folder / stored
    path.write_bytes(data)
    item = Material(batch_id=batch_id, uploaded_by=g.current_user_id, title=title[:255],
                    material_type=material_type[:32], file_path=str(path), file_size=len(data))
    db.session.add(item)
    db.session.commit()
    return success(_material(item), "Material uploaded", 201)


@phase8_api.get("/materials")
@authenticated
def list_materials():
    batch_id = request.args.get("batch_id", type=int)
    student = _student()
    if g.current_claims.get("role") == "student":
        batch_id = student.batch_id if student else None
    if batch_id and not _batch_allowed(batch_id):
        return failure("Forbidden", 403)
    statement = db.select(Material).order_by(Material.created_at.desc(), Material.id.desc())
    if batch_id:
        statement = statement.where(Material.batch_id == batch_id)
    return success([_material(item) for item in db.session.scalars(statement)])


@phase8_api.get("/materials/<int:material_id>/download")
@authenticated
def download_material(material_id):
    item = db.session.get(Material, material_id)
    if not item or not _batch_allowed(item.batch_id):
        return failure("Material not found", 404)
    path = Path(item.file_path).resolve()
    root = Path(current_app.config["UPLOAD_DIR"]).resolve()
    if root not in path.parents or not path.is_file():
        return failure("Material file not found", 404)
    return send_file(path, as_attachment=True, download_name=f"{secure_filename(item.title)}{path.suffix}")


@phase8_api.delete("/materials/<int:material_id>")
@roles_required("superadmin", "staff")
def delete_material(material_id):
    item = db.session.get(Material, material_id)
    if not item or not _batch_allowed(item.batch_id):
        return failure("Material not found", 404)
    path = Path(item.file_path)
    if path.is_file():
        path.unlink()
    db.session.delete(item)
    db.session.commit()
    return success(message="Material deleted")


def _notification_visible(item):
    role = g.current_claims.get("role")
    if item.audience in {"all", role}:
        return True
    if item.audience == "user":
        return item.audience_ref_id == g.current_user_id
    student = _student()
    return item.audience == "batch" and student is not None and item.audience_ref_id == student.batch_id


def _notification(item):
    read = db.session.scalar(db.select(NotificationRead).where(
        NotificationRead.notification_id == item.id, NotificationRead.user_id == g.current_user_id))
    return {"id": item.id, "title": item.title, "message": item.message, "audience": item.audience,
            "created_at": item.created_at.isoformat() if item.created_at else None, "is_read": read is not None}


@phase8_api.post("/notifications")
@roles_required("superadmin", "staff")
def create_notification():
    body = request.get_json(silent=True) or {}
    audience = str(body.get("audience", "all")).strip().lower()
    if audience not in {"all", "superadmin", "staff", "student", "user", "batch"} or not body.get("title") or not body.get("message"):
        return failure("Validation failed", 422)
    item = Notification(title=str(body["title"])[:255], message=str(body["message"]),
                        audience=audience, audience_ref_id=body.get("audience_ref_id"),
                        created_by=g.current_user_id)
    db.session.add(item)
    db.session.commit()
    return success(_notification(item), "Notification created", 201)


@phase8_api.get("/notifications")
@authenticated
def list_notifications():
    items = [item for item in db.session.scalars(db.select(Notification).order_by(Notification.created_at.desc())).all()
             if _notification_visible(item)]
    unread = sum(not _notification(item)["is_read"] for item in items)
    return success([_notification(item) for item in items], meta={"unread": unread})


@phase8_api.get("/notifications/mine")
@authenticated
def list_my_notifications():
    return list_notifications()


@phase8_api.get("/notifications/unread")
@authenticated
def unread_notifications():
    items = [item for item in db.session.scalars(db.select(Notification).order_by(Notification.created_at.desc())).all()
             if _notification_visible(item) and not db.session.scalar(db.select(NotificationRead).where(
                 NotificationRead.notification_id == item.id, NotificationRead.user_id == g.current_user_id))]
    return success([_notification(item) for item in items], meta={"count": len(items)})


@phase8_api.post("/notifications/<int:notification_id>/read")
@authenticated
def mark_notification_read(notification_id):
    item = db.session.get(Notification, notification_id)
    if not item or not _notification_visible(item):
        return failure("Notification not found", 404)
    if not db.session.get(NotificationRead, (notification_id, g.current_user_id)):
        db.session.add(NotificationRead(notification_id=notification_id, user_id=g.current_user_id,
                                        read_at=datetime.now(timezone.utc)))
        db.session.commit()
    return success(message="Notification marked as read")


@phase8_api.post("/notifications/read-all")
@authenticated
def mark_all_notifications_read():
    items = [item for item in db.session.scalars(db.select(Notification)).all()
             if _notification_visible(item)]
    existing = {
        row.notification_id for row in db.session.scalars(
            db.select(NotificationRead).where(NotificationRead.user_id == g.current_user_id)
        ).all()
    }
    now = datetime.now(timezone.utc)
    db.session.add_all(
        NotificationRead(notification_id=item.id, user_id=g.current_user_id, read_at=now)
        for item in items if item.id not in existing
    )
    db.session.commit()
    return success(message="Notifications marked as read")


@phase8_api.get("/settings/public")
def public_settings():
    keys = request.args.get("keys", "").split(",") if request.args.get("keys") else []
    statement = db.select(Setting).order_by(Setting.key)
    if keys:
        statement = statement.where(Setting.key.in_([key.strip() for key in keys if key.strip()]))
    return success({item.key: item.value for item in db.session.scalars(statement)})


@phase8_api.get("/settings")
@roles_required("superadmin")
def get_settings():
    return success({item.key: item.value for item in db.session.scalars(db.select(Setting).order_by(Setting.key))})


@phase8_api.put("/settings")
@phase8_api.patch("/settings")
@roles_required("superadmin")
def update_settings():
    values = request.get_json(silent=True) or {}
    if not isinstance(values, dict):
        return failure("Settings must be an object", 422)
    for key, value in values.items():
        if not isinstance(key, str) or not key.strip() or len(key) > 128:
            return failure("Invalid setting key", 422)
        item = db.session.scalar(db.select(Setting).where(Setting.key == key.strip()))
        if item:
            item.value = value
        else:
            db.session.add(Setting(key=key.strip(), value=value))
    db.session.commit()
    return success({item.key: item.value for item in db.session.scalars(db.select(Setting).order_by(Setting.key))},
                   "Settings updated")


@phase8_api.get("/settings/backup")
@roles_required("superadmin")
def settings_backup():
    settings = {item.key: item.value for item in db.session.scalars(db.select(Setting).order_by(Setting.key))}
    return success({"settings": settings, "exported_at": datetime.now(timezone.utc).isoformat()})


def _dashboard(role):
    if role == "student":
        student = _student()
        attendance = db.session.scalar(db.select(func.count(Attendance.id)).where(Attendance.student_id == student.id)) if student else 0
        dues = db.session.scalar(db.select(func.coalesce(func.sum(Installment.amount - Installment.paid_amount), 0))
                                 .join(FeePlan).where(FeePlan.student_id == student.id)) if student else 0
        return {"role": role, "student": student.name if student else None, "attendance_sessions": attendance, "outstanding_dues": str(dues)}
    recent = db.session.scalars(
        db.select(Student).order_by(Student.created_at.desc()).limit(5)
    ).all()
    drives = db.session.execute(
        db.select(PlacementDrive, Company).join(Company).where(
            PlacementDrive.drive_date >= date.today()
        ).order_by(PlacementDrive.drive_date).limit(5)
    ).all()
    dues = db.session.execute(
        db.select(Installment, Student).join(FeePlan, FeePlan.id == Installment.fee_plan_id)
        .join(Student, Student.id == FeePlan.student_id)
        .where(Installment.status.in_(["pending", "partial", "overdue"]))
        .order_by(Installment.due_date).limit(5)
    ).all()
    lead_counts = db.session.execute(
        db.select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
    ).all()
    admissions_totals = {}
    for item in db.session.scalars(
        db.select(Student).where(Student.admission_date.is_not(None)).order_by(Student.admission_date)
    ).all():
        key = item.admission_date.strftime("%Y-%m")
        admissions_totals[key] = admissions_totals.get(key, 0) + 1
    return {
        "role": role,
        "students": db.session.scalar(db.select(func.count(Student.id))),
        "active_batches": db.session.scalar(db.select(func.count(Batch.id)).where(Batch.status == "active")),
        "courses": db.session.scalar(db.select(func.count(Course.id)).where(Course.is_active.is_(True))),
        "leads": db.session.scalar(db.select(func.count(Lead.id)).where(Lead.status.not_in(["converted", "lost"]))),
        "recent_admissions": [[item.name, str(item.course_id or "-"), str(item.batch_id or "-"), item.status] for item in recent],
        "drives": [[company.name, drive.drive_date.isoformat(), str(db.session.scalar(db.select(func.count(Application.id)).where(Application.drive_id == drive.id)))] for drive, company in drives],
        "dues": [[student.name, installment.due_date.isoformat(), str(installment.amount - installment.paid_amount), installment.status] for installment, student in dues],
        "lead_series": {"labels": [row[0] for row in lead_counts], "datasets": [{"data": [row[1] for row in lead_counts]}]},
        "admissions_series": {"labels": list(admissions_totals), "datasets": [{"label": "Admissions", "data": list(admissions_totals.values()), "backgroundColor": "#0f8b8d"}]},
    }


@phase8_api.get("/dashboard")
@authenticated
def dashboard():
    return success(_dashboard(g.current_claims.get("role")))


@phase8_api.get("/dashboard/superadmin")
@roles_required("superadmin")
def superadmin_dashboard():
    return success(_dashboard("superadmin"))


@phase8_api.get("/dashboard/<role>")
@authenticated
def role_dashboard(role):
    if role != g.current_claims.get("role") and g.current_claims.get("role") != "superadmin":
        return failure("Forbidden", 403)
    if role not in {"superadmin", "staff", "student"}:
        return failure("Unknown dashboard", 404)
    return success(_dashboard(role))


def _csv_response(rows, headers, filename):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return current_app.response_class(output.getvalue(), mimetype="text/csv",
                                      headers={"Content-Disposition": f"attachment; filename={filename}"})


@phase8_api.get("/reports/attendance")
@roles_required("superadmin", "staff")
def attendance_report():
    start, end = _date(request.args.get("from")), _date(request.args.get("to"))
    if (request.args.get("from") and start is None) or (request.args.get("to") and end is None) or (start and end and start > end):
        return failure("Invalid date filter; use YYYY-MM-DD", 422)
    statement = db.select(Attendance, Student.name).join(Student).order_by(Attendance.date)
    if start: statement = statement.where(Attendance.date >= start)
    if end: statement = statement.where(Attendance.date <= end)
    records = db.session.execute(statement).all()
    rows = [[item.name, attendance.date.isoformat(), attendance.status] for attendance, item in records]
    if request.args.get("format") == "csv":
        return _csv_response(rows, ["student", "date", "status"], "attendance-report.csv")
    return success([{"student": row[0], "date": row[1], "status": row[2]} for row in rows])


@phase8_api.get("/reports/fees")
@roles_required("superadmin", "staff")
def fees_report():
    start, end = _date(request.args.get("from")), _date(request.args.get("to"))
    if (request.args.get("from") and start is None) or (request.args.get("to") and end is None) or (start and end and start > end):
        return failure("Invalid date filter; use YYYY-MM-DD", 422)
    statement = db.select(Payment, Student.name).join(Student).order_by(Payment.created_at)
    if start: statement = statement.where(func.date(Payment.created_at) >= start)
    if end: statement = statement.where(func.date(Payment.created_at) <= end)
    records = db.session.execute(statement).all()
    rows = [[item.name, payment.receipt_no, str(payment.amount), payment.status] for payment, item in records]
    if request.args.get("format") == "csv":
        return _csv_response(rows, ["student", "receipt_no", "amount", "status"], "fees-report.csv")
    return success([{"student": row[0], "receipt_no": row[1], "amount": row[2], "status": row[3]} for row in rows])


@phase8_api.get("/reports/admissions")
@roles_required("superadmin")
def admissions_report():
    students = db.session.scalars(
        db.select(Student).where(Student.admission_date.is_not(None)).order_by(Student.admission_date)
    ).all()
    totals = {}
    for student in students:
        key = student.admission_date.strftime("%Y-%m")
        totals[key] = totals.get(key, 0) + 1
    labels = list(totals)
    values = list(totals.values())
    return success({
        "labels": labels,
        "datasets": [{"label": "Admissions", "data": values, "backgroundColor": "#0f8b8d"}],
        "stats": [{"label": "Total admissions", "value": sum(values)}],
        "conversion": [],
        "forecast": [],
    })
