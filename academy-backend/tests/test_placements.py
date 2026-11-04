from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Batch, Course, Student, User


def _token(client, identifier, role, password="password123"):
    response = client.post(
        "/api/v1/auth/login",
        json={"role": role, "userId": identifier, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.get_json()['data']['access_token']}"}


def test_drive_application_eligibility_and_duplicate_protection(client, app):
    with app.app_context():
        user = User(
            login_id="placement-student",
            email="placement-student@example.com",
            password_hash=generate_password_hash("password123"),
            role="student",
        )
        course = Course(name="Placement Python", code="PL-PY", duration_months=6, total_fee=1000)
        db.session.add_all([user, course])
        db.session.flush()
        batch = Batch(code="PL-01", course_id=course.id, capacity=10)
        db.session.add(batch)
        db.session.flush()
        student = Student(
            user_id=user.id, student_code="PL-STU", name="Placement Student",
            course_id=course.id, batch_id=batch.id,
        )
        db.session.add(student)
        db.session.commit()
        course_id = course.id

    admin = _token(client, "admin@example.com", "superadmin")
    company = client.post("/api/v1/companies", headers=admin, json={"name": "Acme"})
    assert company.status_code == 201
    company_id = company.get_json()["data"]["id"]
    drive = client.post(
        "/api/v1/drives", headers=admin,
        json={"company_id": company_id, "title": "Python Engineer", "role": "Engineer",
              "drive_date": "2026-12-01", "course_id": course_id},
    )
    assert drive.status_code == 201

    student_headers = _token(client, "placement-student", "student")
    # The course id is deliberately obtained from the drive response to avoid
    # relying on database primary-key allocation in the test fixture.
    drive_id = drive.get_json()["data"]["id"]
    response = client.post("/api/v1/applications", headers=student_headers, json={"drive_id": drive_id})
    assert response.status_code == 201
    duplicate = client.post("/api/v1/applications", headers=student_headers, json={"drive_id": drive_id})
    assert duplicate.status_code == 409
    assert client.get("/api/v1/me/applications", headers=student_headers).status_code == 200


def test_placement_application_blocks_low_attendance(client, app):
    with app.app_context():
        user = User(
            login_id="low-attendance-student",
            email="low-attendance@example.com",
            password_hash=generate_password_hash("password123"),
            role="student",
        )
        course = Course(name="Low Attendance", code="LOW-ATT", duration_months=6, total_fee=1000)
        db.session.add_all([user, course])
        db.session.flush()
        batch = Batch(code="LOW-01", course_id=course.id, capacity=10)
        db.session.add(batch)
        db.session.flush()
        student = Student(
            user_id=user.id,
            student_code="LOW-STU",
            name="Low Attendance Student",
            course_id=course.id,
            batch_id=batch.id,
        )
        db.session.add(student)
        db.session.commit()
        course_id = course.id

    admin = _token(client, "admin@example.com", "superadmin")
    company = client.post("/api/v1/companies", headers=admin, json={"name": "Low Attendance Co"})
    assert company.status_code == 201
    drive = client.post(
        "/api/v1/drives",
        headers=admin,
        json={
            "company_id": company.get_json()["data"]["id"],
            "title": "Attendance-gated role",
            "role": "Engineer",
            "drive_date": "2026-12-01",
            "course_id": course_id,
            "attendance_threshold": 75,
        },
    )
    assert drive.status_code == 201
    student_headers = _token(client, "low-attendance-student", "student")
    response = client.post(
        "/api/v1/applications",
        headers=student_headers,
        json={"drive_id": drive.get_json()["data"]["id"]},
    )
    assert response.status_code == 422
    assert response.get_json()["errors"]["attendance"] == 0.0
