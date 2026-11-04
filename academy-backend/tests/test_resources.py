from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User


def _token(client, role="superadmin", identifier="admin@example.com", password="password123"):
    response = client.post(
        "/api/v1/auth/login",
        json={"role": role, "userId": identifier, "password": password},
    )
    return response.get_json()["data"]["access_token"]


def test_superadmin_can_create_and_list_courses(client):
    headers = {"Authorization": f"Bearer {_token(client)}"}
    created = client.post(
        "/api/v1/courses",
        headers=headers,
        json={"name": "Python Full Stack", "code": "PFS", "duration_months": 6, "total_fee": 45000},
    )
    assert created.status_code == 201
    listed = client.get("/api/v1/courses?page=1&per_page=10", headers=headers)
    assert listed.status_code == 200
    assert listed.get_json()["meta"]["total"] == 1


def test_student_cannot_read_another_student(client, app):
    with app.app_context():
        user = User(
            email="student@example.com",
            login_id="STU-1",
            password_hash=generate_password_hash("password123"),
            role="student",
        )
        other = User(
            email="other@example.com",
            login_id="STU-OTHER",
            password_hash=generate_password_hash("password123"),
            role="student",
        )
        db.session.add_all([user, other])
        db.session.commit()
        from app.models import Student

        db.session.add_all(
            [
                Student(user_id=user.id, student_code="STU-1-001", name="Student One"),
                Student(user_id=other.id, student_code="STU-1-002", name="Student Two"),
            ]
        )
        db.session.commit()
        other_id = db.session.query(Student).filter_by(user_id=other.id).one().id
    headers = {"Authorization": f"Bearer {_token(client, 'student', 'STU-1')}"}
    response = client.get(f"/api/v1/students/{other_id}", headers=headers)
    assert response.status_code == 403


def test_student_cannot_create_course(client, app):
    with app.app_context():
        db.session.add(
            User(
                email="student2@example.com",
                login_id="STU-2",
                password_hash=generate_password_hash("password123"),
                role="student",
            )
        )
        db.session.commit()
    headers = {"Authorization": f"Bearer {_token(client, 'student', 'STU-2')}"}
    response = client.post(
        "/api/v1/courses",
        headers=headers,
        json={"name": "Unauthorized", "code": "NO", "duration_months": 1, "total_fee": 1},
    )
    assert response.status_code == 403
