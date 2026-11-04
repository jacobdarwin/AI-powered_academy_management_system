import pytest
from datetime import datetime, timezone, timedelta
from freezegun import freeze_time

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from werkzeug.security import generate_password_hash
from app.models import Batch, Course, Staff, Student, User


@pytest.fixture()
def app():
    application = create_app(TestingConfig)
    with application.app_context():
        db.create_all()
        db.session.add(
            User(
                email="admin@example.com",
                login_id="admin@example.com",
                password_hash=generate_password_hash("password123"),
                role="superadmin",
            )
        )
        db.session.commit()
        yield application
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def frozen_time():
    with freeze_time("2026-11-03 12:00:00+00:00"):
        yield


@pytest.fixture()
def actors(app):
    with app.app_context():
        course_a = Course(name="Python", code="PY-TEST", duration_months=6, total_fee=1000)
        course_b = Course(name="Java", code="JAVA-TEST", duration_months=6, total_fee=1000)
        db.session.add_all([course_a, course_b])
        db.session.flush()

        actor_specs = [
            ("trainer-a@example.com", "STF-TRAINER-A", "staff", "trainer", True, None),
            ("trainer-b@example.com", "STF-TRAINER-B", "staff", "trainer", True, None),
            ("counselor@example.com", "STF-COUNSELOR", "staff", "counselor", True, None),
            ("placement@example.com", "STF-PLACEMENT", "staff", "placement_officer", True, None),
            ("accounts@example.com", "STF-ACCOUNTS", "staff", "accounts", True, None),
            ("student-a@example.com", "STU-TEST-A", "student", None, True, None),
            ("student-b@example.com", "STU-TEST-B", "student", None, True, None),
            ("inactive@example.com", "STU-INACTIVE", "student", None, False, None),
            ("locked@example.com", "STU-LOCKED", "student", None, True, datetime.now(timezone.utc) + timedelta(minutes=15)),
        ]
        users = {}
        staff = {}
        for email, login_id, role, designation, active, locked_until in actor_specs:
            user = User(
                email=email,
                login_id=login_id,
                password_hash=generate_password_hash("password123"),
                role=role,
                is_active=active,
                locked_until=locked_until,
            )
            db.session.add(user)
            db.session.flush()
            users[login_id] = user
            if role == "staff":
                staff[login_id] = Staff(
                    user_id=user.id,
                    staff_code=login_id,
                    name=login_id,
                    designation=designation,
                )
                db.session.add(staff[login_id])
        db.session.flush()

        batch_a = Batch(code="PY-TEST-01", course_id=course_a.id, trainer_id=staff["STF-TRAINER-A"].id, capacity=10)
        batch_b = Batch(code="JAVA-TEST-01", course_id=course_b.id, trainer_id=staff["STF-TRAINER-B"].id, capacity=10)
        db.session.add_all([batch_a, batch_b])
        db.session.flush()
        student_a = Student(
            user_id=users["STU-TEST-A"].id,
            student_code="STU-TEST-A",
            name="Student A",
            course_id=course_a.id,
            batch_id=batch_a.id,
        )
        student_b = Student(
            user_id=users["STU-TEST-B"].id,
            student_code="STU-TEST-B",
            name="Student B",
            course_id=course_b.id,
            batch_id=batch_b.id,
        )
        db.session.add_all([student_a, student_b])
        db.session.commit()
        return {
            "users": {login_id: user.id for login_id, user in users.items()},
            "staff": {login_id: item.id for login_id, item in staff.items()},
            "batches": {"a": batch_a.id, "b": batch_b.id},
            "students": {"a": student_a.id, "b": student_b.id},
            "password": "password123",
        }


@pytest.fixture()
def auth_headers(client):
    cache = {}

    def make(login_id, role, password="password123"):
        cache_key = (login_id, role, password)
        if cache_key in cache:
            return cache[cache_key]
        response = client.post(
            "/api/v1/auth/login",
            json={"role": role, "userId": login_id, "password": password},
        )
        assert response.status_code == 200
        cache[cache_key] = {
            "Authorization": f"Bearer {response.get_json()['data']['access_token']}"
        }
        return cache[cache_key]

    make.clear = cache.clear
    return make
