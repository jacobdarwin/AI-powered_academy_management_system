from datetime import date, timedelta
from decimal import Decimal
import os

from flask import current_app
from werkzeug.security import generate_password_hash

from .extensions import db
from .models import (
    Assessment,
    Attendance,
    Batch,
    Company,
    Course,
    FeePlan,
    Installment,
    Lead,
    Mark,
    PlacementDrive,
    Staff,
    Student,
    User,
)


def seed_demo() -> None:
    if os.getenv("FLASK_ENV", "development").lower() == "production":
        raise RuntimeError("The demo seed is disabled in production.")

    admin = db.session.scalar(db.select(User).where(User.login_id == "admin@youracademy.com"))
    if admin is None:
        admin = User(
            email="admin@youracademy.com",
            login_id="admin@youracademy.com",
            password_hash=generate_password_hash("Admin@12345"),
            role="superadmin",
        )
        db.session.add(admin)
        db.session.flush()

    designations = ["trainer", "counselor", "placement_officer", "accounts"]
    staff_by_designation = {}
    for index, designation in enumerate(designations, 1):
        login_id = f"STF-{index:04d}"
        user = db.session.scalar(db.select(User).where(User.login_id == login_id))
        if user is None:
            user = User(
                login_id=login_id,
                email=f"{designation}@youracademy.com",
                password_hash=generate_password_hash("Staff@12345"),
                role="staff",
            )
            db.session.add(user)
            db.session.flush()
        staff = db.session.scalar(db.select(Staff).where(Staff.user_id == user.id))
        if staff is None:
            staff = Staff(
                user_id=user.id,
                staff_code=login_id,
                name=designation.replace("_", " ").title(),
                designation=designation,
            )
            db.session.add(staff)
            db.session.flush()
        staff_by_designation[designation] = staff

    course_data = [
        ("Python Full Stack", "PFS", 6, 45000),
        ("Java Full Stack", "JFS", 6, 45000),
        ("Data Science and AI", "DS", 8, 60000),
        ("Digital Marketing", "DM", 4, 25000),
    ]
    courses = []
    for name, code, months, fee in course_data:
        course = db.session.scalar(db.select(Course).where(Course.code == code))
        if course is None:
            course = Course(
                name=name,
                code=code,
                duration_months=months,
                total_fee=Decimal(fee),
            )
            db.session.add(course)
            db.session.flush()
        courses.append(course)

    batches = []
    for index, course in enumerate(courses, 1):
        code = f"{course.code}-{index:02d}"
        batch = db.session.scalar(db.select(Batch).where(Batch.code == code))
        if batch is None:
            batch = Batch(
                code=code,
                course_id=course.id,
                trainer_id=staff_by_designation["trainer"].id,
                schedule="Mon-Fri 09:00-11:00",
                start_date=date.today() - timedelta(days=30),
                capacity=30,
                status="running",
            )
            db.session.add(batch)
            db.session.flush()
        batches.append(batch)

    for index in range(1, 41):
        code = f"STU-2026-{index:04d}"
        user = db.session.scalar(db.select(User).where(User.login_id == code))
        if user is None:
            user = User(
                login_id=code,
                email=f"student{index}@youracademy.com",
                password_hash=generate_password_hash("Student@12345"),
                role="student",
                must_change_password=False,
            )
            db.session.add(user)
            db.session.flush()
        student = db.session.scalar(db.select(Student).where(Student.student_code == code))
        batch = batches[(index - 1) % len(batches)]
        course = courses[(index - 1) % len(courses)]
        if student is None:
            student = Student(
                user_id=user.id,
                student_code=code,
                name=f"Demo Student {index}",
                email=user.email,
                phone=f"900000{index:04d}",
                course_id=course.id,
                batch_id=batch.id,
                admission_date=date.today() - timedelta(days=45),
            )
            db.session.add(student)
            db.session.flush()
        plan = db.session.scalar(db.select(FeePlan).where(FeePlan.student_id == student.id))
        if plan is None:
            plan = FeePlan(student_id=student.id, final_amount=course.total_fee)
            db.session.add(plan)
            db.session.flush()
            db.session.add(
                Installment(
                    fee_plan_id=plan.id,
                    label="Admission installment",
                    due_date=date.today() - timedelta(days=10),
                    amount=course.total_fee / 2,
                    paid_amount=course.total_fee / 2,
                    status="paid",
                )
            )
            db.session.add(
                Installment(
                    fee_plan_id=plan.id,
                    label="Final installment",
                    due_date=date.today() + timedelta(days=30),
                    amount=course.total_fee / 2,
                )
            )

    for index in range(1, 31):
        phone = f"880000{index:04d}"
        if db.session.scalar(db.select(Lead).where(Lead.phone == phone)) is None:
            db.session.add(
                Lead(
                    name=f"Demo Lead {index}",
                    phone=phone,
                    email=f"lead{index}@example.com",
                    course_id=courses[(index - 1) % len(courses)].id,
                    source="website",
                    counselor_id=staff_by_designation["counselor"].id,
                )
            )

    for index in range(1, 7):
        name = f"Demo Company {index}"
        company = db.session.scalar(db.select(Company).where(Company.name == name))
        if company is None:
            company = Company(name=name, website=f"https://company{index}.example.com")
            db.session.add(company)
            db.session.flush()
        if db.session.scalar(db.select(PlacementDrive).where(PlacementDrive.title == f"Drive {index}")) is None:
            db.session.add(
                PlacementDrive(
                    company_id=company.id,
                    title=f"Drive {index}",
                    role="Software Engineer",
                    drive_date=date.today() + timedelta(days=index * 7),
                    package=Decimal("600000"),
                    course_id=courses[(index - 1) % len(courses)].id,
                    attendance_threshold=Decimal("75"),
                    marks_threshold=Decimal("60"),
                )
            )

    db.session.commit()
