from ..extensions import db
from .base import SoftDeleteMixin, TimestampMixin


class User(TimestampMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)
    login_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    must_change_password = db.Column(db.Boolean, nullable=False, default=False)
    last_login_at = db.Column(db.DateTime(timezone=True))
    failed_login_count = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime(timezone=True))


class PasswordResetToken(TimestampMixin, db.Model):
    __tablename__ = "password_reset_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    token_hash = db.Column(db.String(128), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used_at = db.Column(db.DateTime(timezone=True))


class RevokedToken(db.Model):
    __tablename__ = "revoked_tokens"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(64), unique=True, nullable=False, index=True)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=False)


class Course(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    duration_months = db.Column(db.Integer, nullable=False)
    total_fee = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Staff(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "staff"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    staff_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(32))
    designation = db.Column(db.String(32), nullable=False, index=True)
    qualification = db.Column(db.String(255))
    joined_on = db.Column(db.Date)
    salary = db.Column(db.Numeric(10, 2))
    skills = db.Column(db.Text)
    status = db.Column(db.String(32), nullable=False, default="active")
    photo_path = db.Column(db.String(512))


class Batch(TimestampMixin, db.Model):
    __tablename__ = "batches"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey("staff.id"), index=True)
    schedule = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    capacity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(32), nullable=False, default="planned")


class Lead(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "leads"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(32), nullable=False, index=True)
    email = db.Column(db.String(255))
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), index=True)
    source = db.Column(db.String(64))
    counselor_id = db.Column(db.Integer, db.ForeignKey("staff.id"), index=True)
    follow_up_on = db.Column(db.Date)
    note = db.Column(db.Text)
    status = db.Column(db.String(32), nullable=False, default="new", index=True)
    converted_student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id", use_alter=True, name="fk_leads_converted_student"),
    )


class LeadFollowUp(TimestampMixin, db.Model):
    __tablename__ = "lead_follow_ups"
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=False, index=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=True, index=True)
    follow_up_on = db.Column(db.Date, nullable=False)
    note = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(32), nullable=False, default="planned")


class Student(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    student_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(32))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(32))
    address = db.Column(db.Text)
    guardian_name = db.Column(db.String(160))
    guardian_phone = db.Column(db.String(32))
    qualification = db.Column(db.String(255))
    college = db.Column(db.String(255))
    year_of_passing = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), index=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), index=True)
    admission_date = db.Column(db.Date)
    status = db.Column(db.String(32), nullable=False, default="active", index=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"))
    photo_path = db.Column(db.String(512))
    resume_path = db.Column(db.String(512))
    placed_status = db.Column(db.String(32), nullable=False, default="not_placed")


class Attendance(TimestampMixin, db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(16), nullable=False)
    note = db.Column(db.Text)
    __table_args__ = (db.UniqueConstraint("student_id", "date", name="uq_attendance_student_date"),)


class FeePlan(TimestampMixin, db.Model):
    __tablename__ = "fee_plans"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    final_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="active")


class Installment(TimestampMixin, db.Model):
    __tablename__ = "installments"
    id = db.Column(db.Integer, primary_key=True)
    fee_plan_id = db.Column(db.Integer, db.ForeignKey("fee_plans.id"), nullable=False, index=True)
    label = db.Column(db.String(128), nullable=False)
    due_date = db.Column(db.Date, nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(32), nullable=False, default="pending")


class Payment(TimestampMixin, db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    installment_id = db.Column(db.Integer, db.ForeignKey("installments.id"), index=True)
    receipt_no = db.Column(db.String(64), unique=True, nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    mode = db.Column(db.String(32), nullable=False)
    reference = db.Column(db.String(128))
    status = db.Column(db.String(16), nullable=False, default="paid")
    void_reason = db.Column(db.Text)


class Expense(TimestampMixin, db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(128), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    note = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class Assessment(TimestampMixin, db.Model):
    __tablename__ = "assessments"
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    assessment_type = db.Column(db.String(32), nullable=False)
    max_marks = db.Column(db.Numeric(8, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)


class Mark(TimestampMixin, db.Model):
    __tablename__ = "marks"
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    marks_obtained = db.Column(db.Numeric(8, 2), nullable=False)
    feedback = db.Column(db.Text)
    __table_args__ = (db.UniqueConstraint("assessment_id", "student_id", name="uq_mark_assessment_student"),)


class Material(TimestampMixin, db.Model):
    __tablename__ = "materials"
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False, index=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    material_type = db.Column(db.String(32), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer)


class Company(TimestampMixin, db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True, nullable=False)
    website = db.Column(db.String(255))
    contact = db.Column(db.String(255))


class PlacementDrive(TimestampMixin, db.Model):
    __tablename__ = "placement_drives"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    role = db.Column(db.String(160), nullable=False)
    drive_date = db.Column(db.Date, nullable=False)
    package = db.Column(db.Numeric(10, 2))
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), index=True)
    attendance_threshold = db.Column(db.Numeric(5, 2))
    marks_threshold = db.Column(db.Numeric(5, 2))
    status = db.Column(db.String(32), nullable=False, default="open", index=True)


class Application(TimestampMixin, db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    stage = db.Column(db.String(32), nullable=False, default="applied")
    offer_details = db.Column(db.JSON)
    __table_args__ = (db.UniqueConstraint("drive_id", "student_id", name="uq_application_drive_student"),)


class Certificate(TimestampMixin, db.Model):
    __tablename__ = "certificates"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    certificate_no = db.Column(db.String(64), unique=True, nullable=False)
    issued_on = db.Column(db.Date, nullable=False)
    file_path = db.Column(db.String(512))


class Notification(TimestampMixin, db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    audience = db.Column(db.String(32), nullable=False, index=True)
    audience_ref_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class NotificationRead(db.Model):
    __tablename__ = "notification_reads"
    notification_id = db.Column(db.Integer, db.ForeignKey("notifications.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    read_at = db.Column(db.DateTime(timezone=True), nullable=False)


class Setting(TimestampMixin, db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), unique=True, nullable=False)
    value = db.Column(db.JSON, nullable=False)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    action = db.Column(db.String(64), nullable=False)
    entity = db.Column(db.String(64), nullable=False)
    entity_id = db.Column(db.Integer)
    before = db.Column(db.JSON)
    after = db.Column(db.JSON)
    ip = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)


class FaceEnrollment(TimestampMixin, db.Model):
    __tablename__ = "face_enrollments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), unique=True, nullable=False)
    consented_at = db.Column(db.DateTime(timezone=True), nullable=False)
    vector_reference = db.Column(db.String(512), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
