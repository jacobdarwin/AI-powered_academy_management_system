from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Lead, Staff, User


def _token(client, role, identifier, password="password123"):
    response = client.post(
        "/api/v1/auth/login",
        json={"role": role, "userId": identifier, "password": password},
    )
    assert response.status_code == 200
    return response.get_json()["data"]["access_token"]


def _counselor(app):
    with app.app_context():
        user = User(
            email="counselor@example.com",
            login_id="STF-COUNSELOR",
            password_hash=generate_password_hash("password123"),
            role="staff",
        )
        db.session.add(user)
        db.session.flush()
        db.session.add(
            Staff(
                user_id=user.id,
                staff_code="STF-0002",
                name="Counselor",
                designation="counselor",
            )
        )
        db.session.commit()


def test_lead_conversion_creates_linked_student_and_account(client):
    lead = client.post(
        "/api/v1/leads",
        headers={"Authorization": f"Bearer {_token(client, 'superadmin', 'admin@example.com')}"},
        json={"name": "Asha", "phone": "9999999999", "email": "asha@example.com"},
    )
    assert lead.status_code == 201
    lead_id = lead.get_json()["data"]["id"]
    converted = client.post(
        f"/api/v1/leads/{lead_id}/convert",
        headers={"Authorization": f"Bearer {_token(client, 'superadmin', 'admin@example.com')}"},
        json={"student_code": "STU-2026-0001"},
    )
    assert converted.status_code == 201
    data = converted.get_json()["data"]
    assert data["student"]["student_code"] == "STU-2026-0001"
    assert data["temporary_password"]
    duplicate = client.post(
        f"/api/v1/leads/{lead_id}/convert",
        headers={"Authorization": f"Bearer {_token(client, 'superadmin', 'admin@example.com')}"},
        json={"student_code": "STU-2026-0002"},
    )
    assert duplicate.status_code == 409


def test_counselor_can_only_see_own_leads(client, app):
    _counselor(app)
    token = _token(client, "staff", "STF-COUNSELOR")
    response = client.post(
        "/api/v1/leads",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Counselled", "phone": "8888888888"},
    )
    assert response.status_code == 201
    listed = client.get("/api/v1/leads", headers={"Authorization": f"Bearer {token}"})
    assert listed.get_json()["meta"]["total"] == 1


def test_non_counselor_staff_is_denied(client, app):
    with app.app_context():
        user = User(
            email="trainer@example.com",
            login_id="STF-TRAINER",
            password_hash=generate_password_hash("password123"),
            role="staff",
        )
        db.session.add(user)
        db.session.flush()
        db.session.add(
            Staff(
                user_id=user.id,
                staff_code="STF-0003",
                name="Trainer",
                designation="trainer",
            )
        )
        db.session.commit()
    token = _token(client, "staff", "STF-TRAINER")
    response = client.get("/api/v1/leads", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_follow_up_updates_lead_and_conversion_rolls_back(client):
    headers = {"Authorization": f"Bearer {_token(client, 'superadmin', 'admin@example.com')}"}
    lead = client.post(
        "/api/v1/leads",
        headers=headers,
        json={"name": "Rollback", "phone": "7777777777", "email": "admin@example.com"},
    ).get_json()["data"]
    follow_up = client.post(
        f"/api/v1/leads/{lead['id']}/follow-ups",
        headers=headers,
        json={"follow_up_on": "2026-11-10", "note": "Call again"},
    )
    assert follow_up.status_code == 201
    conversion = client.post(
        f"/api/v1/leads/{lead['id']}/convert",
        headers=headers,
        json={"student_code": "STU-2026-ROLLBACK"},
    )
    assert conversion.status_code == 409
    current = client.get(f"/api/v1/leads/{lead['id']}", headers=headers).get_json()["data"]
    assert current["converted_student_id"] is None
    assert current["status"] == "follow_up"
