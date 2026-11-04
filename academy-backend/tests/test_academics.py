from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Assessment, Batch, Course, Staff, Student, User


def _token(client, role, identifier, password="password123"):
    response = client.post(
        "/api/v1/auth/login",
        json={"role": role, "userId": identifier, "password": password},
    )
    assert response.status_code == 200
    return response.get_json()["data"]["access_token"]


def _fixture_data(app):
    with app.app_context():
        trainer_user = User(
            email="trainer@example.com",
            login_id="STF-TRAINER",
            password_hash=generate_password_hash("password123"),
            role="staff",
        )
        student_user = User(
            email="student@example.com",
            login_id="STU-ONE",
            password_hash=generate_password_hash("password123"),
            role="student",
        )
        other_user = User(
            email="other@example.com",
            login_id="STU-TWO",
            password_hash=generate_password_hash("password123"),
            role="student",
        )
        db.session.add_all([trainer_user, student_user, other_user])
        db.session.flush()
        trainer = Staff(
            user_id=trainer_user.id,
            staff_code="STF-0002",
            name="Trainer",
            designation="trainer",
        )
        course = Course(name="Python", code="PY", duration_months=6, total_fee=1000)
        db.session.add_all([trainer, course])
        db.session.flush()
        batch = Batch(code="PY-01", course_id=course.id, trainer_id=trainer.id, capacity=10)
        db.session.add(batch)
        db.session.flush()
        one = Student(
            user_id=student_user.id,
            student_code="STU-ONE",
            name="Student One",
            course_id=course.id,
            batch_id=batch.id,
        )
        two = Student(
            user_id=other_user.id,
            student_code="STU-TWO",
            name="Student Two",
            course_id=course.id,
            batch_id=batch.id,
        )
        db.session.add_all([one, two])
        db.session.commit()
        return batch.id, one.id, two.id


def test_bulk_attendance_and_percentage(client, app):
    batch_id, one_id, _ = _fixture_data(app)
    admin = {"Authorization": f"Bearer {_token(client, 'superadmin', 'admin@example.com')}"}
    response = client.post(
        "/api/v1/attendance/bulk",
        headers=admin,
        json={
            "batch_id": batch_id,
            "date": "2026-11-02",
            "records": [
                {"student_id": one_id, "status": "present"},
            ],
        },
    )
    assert response.status_code == 200
    response = client.post(
        "/api/v1/attendance/bulk",
        headers=admin,
        json={
            "batch_id": batch_id,
            "date": "2026-11-01",
            "records": [
                {"student_id": one_id, "status": "absent"},
            ],
        },
    )
    assert response.status_code == 200
    summary = client.get(
        f"/api/v1/students/{one_id}/attendance", headers=admin
    ).get_json()["data"]
    assert summary["percentage"] == 50.0
    assert summary["total_sessions"] == 2


def test_future_attendance_and_wrong_batch_are_rejected(client, app):
    batch_id, one_id, _ = _fixture_data(app)
    admin = {"Authorization": f"Bearer {_token(client, 'superadmin', 'admin@example.com')}"}
    future = client.post(
        "/api/v1/attendance/bulk",
        headers=admin,
        json={"batch_id": batch_id, "date": "2999-01-01", "records": []},
    )
    assert future.status_code == 422
    trainer = {"Authorization": f"Bearer {_token(client, 'staff', 'STF-TRAINER')}"}
    allowed = client.post(
        "/api/v1/attendance/bulk",
        headers=trainer,
        json={
            "batch_id": batch_id,
            "date": "2026-11-02",
            "records": [{"student_id": one_id, "status": "late"}],
        },
    )
    assert allowed.status_code == 200


def test_marks_enforce_maximum_and_student_isolation(client, app):
    batch_id, one_id, two_id = _fixture_data(app)
    admin = {"Authorization": f"Bearer {_token(client, 'superadmin', 'admin@example.com')}"}
    assessment = client.post(
        "/api/v1/assessments",
        headers=admin,
        json={
            "batch_id": batch_id,
            "title": "Python test",
            "assessment_type": "test",
            "max_marks": 100,
            "date": "2026-11-01",
        },
    )
    assert assessment.status_code == 201
    assessment_id = assessment.get_json()["data"]["id"]
    invalid = client.post(
        "/api/v1/marks/bulk",
        headers=admin,
        json={"assessment_id": assessment_id, "records": [{"student_id": one_id, "marks": 101}]},
    )
    assert invalid.status_code == 422
    saved = client.post(
        "/api/v1/marks/bulk",
        headers=admin,
        json={"assessment_id": assessment_id, "records": [{"student_id": one_id, "marks": 80}]},
    )
    assert saved.status_code == 200
    student = {"Authorization": f"Bearer {_token(client, 'student', 'STU-ONE')}"}
    marks = client.get(
        f"/api/v1/marks?student_id={two_id}", headers=student
    )
    assert marks.status_code == 200
    assert len(marks.get_json()["data"]) == 1
    assert marks.get_json()["data"][0]["student_id"] == one_id


def test_student_cannot_read_another_students_attendance_or_marks(client, app):
    batch_id, one_id, two_id = _fixture_data(app)
    admin = {"Authorization": f"Bearer {_token(client, "superadmin", "admin@example.com", "password123")}"}
    for attendance_date, status in (("2026-11-01", "present"), ("2026-11-02", "absent")):
        response = client.post(
            "/api/v1/attendance/bulk",
            headers=admin,
            json={
                "batch_id": batch_id,
                "date": attendance_date,
                "records": [{"student_id": two_id, "status": status}],
            },
        )
        assert response.status_code == 200
    assessment = client.post(
        "/api/v1/assessments",
        headers=admin,
        json={
            "batch_id": batch_id,
            "title": "Isolation test",
            "assessment_type": "test",
            "max_marks": 100,
            "date": "2026-11-01",
        },
    )
    assert assessment.status_code == 201
    response = client.post(
        "/api/v1/marks/bulk",
        headers=admin,
        json={
            "assessment_id": assessment.get_json()["data"]["id"],
            "records": [{"student_id": two_id, "marks": 88}],
        },
    )
    assert response.status_code == 200

    student = {"Authorization": f"Bearer {_token(client, "student", "STU-ONE", "password123")}"}
    attendance = client.get(
        f"/api/v1/students/{two_id}/attendance", headers=student
    )
    assert attendance.status_code == 403
    marks = client.get(f"/api/v1/marks?student_id={two_id}", headers=student)
    assert marks.status_code == 200
    assert marks.get_json()["data"] == []


def test_trainer_cannot_mark_attendance_or_enter_marks_for_unassigned_batch(client, app):
    batch_id, one_id, _ = _fixture_data(app)
    with app.app_context():
        other_course = Course(name="Java", code="JAVA", duration_months=6, total_fee=1000)
        other_trainer_user = User(
            email="other-trainer@example.com",
            login_id="STF-OTHER",
            password_hash=generate_password_hash("password123"),
            role="staff",
        )
        db.session.add_all([other_course, other_trainer_user])
        db.session.flush()
        other_trainer = Staff(
            user_id=other_trainer_user.id,
            staff_code="STF-0003",
            name="Other Trainer",
            designation="trainer",
        )
        db.session.add(other_trainer)
        db.session.flush()
        other_batch = Batch(
            code="JAVA-01",
            course_id=other_course.id,
            trainer_id=other_trainer.id,
            capacity=10,
        )
        db.session.add(other_batch)
        db.session.commit()
        other_batch_id = other_batch.id

    admin = {"Authorization": f"Bearer {_token(client, "superadmin", "admin@example.com", "password123")}"}
    assessment = client.post(
        "/api/v1/assessments",
        headers=admin,
        json={
            "batch_id": other_batch_id,
            "title": "Other batch test",
            "assessment_type": "test",
            "max_marks": 100,
            "date": "2026-11-01",
        },
    )
    assert assessment.status_code == 201
    trainer = {"Authorization": f"Bearer {_token(client, "staff", "STF-TRAINER", "password123")}"}
    attendance = client.post(
        "/api/v1/attendance/bulk",
        headers=trainer,
        json={
            "batch_id": other_batch_id,
            "date": "2026-11-02",
            "records": [{"student_id": one_id, "status": "present"}],
        },
    )
    assert attendance.status_code == 403
    marks = client.post(
        "/api/v1/marks/bulk",
        headers=trainer,
        json={
            "assessment_id": assessment.get_json()["data"]["id"],
            "records": [{"student_id": one_id, "marks": 75}],
        },
    )
    assert marks.status_code == 403
