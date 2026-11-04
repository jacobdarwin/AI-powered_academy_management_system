from io import BytesIO

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Batch, Course, Notification, Staff, User


def _auth(app, user_id, role, designation=None):
    with app.app_context():
        claims = {"role": role}
        if designation:
            claims["designation"] = designation
        return {"Authorization": f"Bearer {create_access_token(str(user_id), additional_claims=claims)}"}


def test_settings_and_notifications(client, app):
    with app.app_context():
        admin = db.session.scalar(db.select(User).where(User.login_id == "admin@example.com"))
        headers = _auth(app, admin.id, "superadmin")
    response = client.put("/api/v1/settings", headers=headers, json={"academy_name": "Test Academy"})
    assert response.status_code == 200
    assert client.get("/api/v1/settings/public").get_json()["data"]["academy_name"] == "Test Academy"
    created = client.post("/api/v1/notifications", headers=headers,
                          json={"title": "Welcome", "message": "Hello", "audience": "all"})
    assert created.status_code == 201
    assert client.get("/api/v1/notifications/unread", headers=headers).get_json()["meta"]["count"] == 1


def test_material_upload_download_and_delete(client, app):
    with app.app_context():
        admin = db.session.scalar(db.select(User).where(User.login_id == "admin@example.com"))
        course = Course(name="Python", code="PY", duration_months=3, total_fee=100)
        db.session.add(course)
        db.session.flush()
        batch = Batch(code="B1", course_id=course.id, capacity=10)
        db.session.add(batch)
        db.session.commit()
        headers = _auth(app, admin.id, "superadmin")
        batch_id = batch.id
    uploaded = client.post("/api/v1/materials", headers=headers, data={
        "batch_id": str(batch_id), "title": "Guide", "file": (BytesIO(b"safe"), "guide.txt")
    }, content_type="multipart/form-data")
    assert uploaded.status_code == 201
    material_id = uploaded.get_json()["data"]["id"]
    assert client.get(f"/api/v1/materials/{material_id}/download", headers=headers).data == b"safe"
    assert client.delete(f"/api/v1/materials/{material_id}", headers=headers).status_code == 200
    assert client.get(f"/api/v1/materials/{material_id}/download", headers=headers).status_code == 404


def test_material_rejects_unsafe_extension(client, app):
    with app.app_context():
        admin = db.session.scalar(db.select(User).where(User.login_id == "admin@example.com"))
        course = Course(name="Java", code="JV", duration_months=3, total_fee=100)
        db.session.add(course)
        db.session.flush()
        batch = Batch(code="B2", course_id=course.id, capacity=10)
        db.session.add(batch)
        db.session.commit()
        batch_id = batch.id
        headers = _auth(app, admin.id, "superadmin")
    response = client.post("/api/v1/materials", headers=headers, data={
        "batch_id": str(batch_id), "title": "Bad", "file": (BytesIO(b"x"), "bad.exe")
    }, content_type="multipart/form-data")
    assert response.status_code == 422
