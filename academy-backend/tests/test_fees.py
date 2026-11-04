from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app import create_app
from app.config import TestingConfig
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import FeePlan, Installment, Student, User


def _token(client, role, identifier, password="password123"):
    response = client.post(
        "/api/v1/auth/login",
        json={"role": role, "userId": identifier, "password": password},
    )
    assert response.status_code == 200
    return response.get_json()["data"]["access_token"]


def _student(app):
    with app.app_context():
        user = User(
            email="fee-student@example.com",
            login_id="STU-FEE",
            password_hash=generate_password_hash("password123"),
            role="student",
        )
        db.session.add(user)
        db.session.flush()
        student = Student(
            user_id=user.id,
            student_code="STU-FEE",
            name="Fee Student",
            email=user.email,
        )
        db.session.add(student)
        db.session.commit()
        return student.id


def _plan(client, token, student_id):
    response = client.post(
        "/api/v1/fees/plans",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "student_id": student_id,
            "final_amount": 1000,
            "installments": [
                {"label": "First", "due_date": "2026-11-01", "amount": 600},
                {"label": "Second", "due_date": "2026-12-01", "amount": 400},
            ],
        },
    )
    assert response.status_code == 201
    return response.get_json()["data"]


def test_fee_plan_payment_receipt_and_status(client, app):
    student_id = _student(app)
    admin = _token(client, "superadmin", "admin@example.com")
    plan = _plan(client, admin, student_id)
    installment_id = plan["installments"][0]["id"]
    payment = client.post(
        "/api/v1/fees/payments",
        headers={"Authorization": f"Bearer {admin}"},
        json={
            "student_id": student_id,
            "installment_id": installment_id,
            "amount": 600,
            "mode": "cash",
        },
    )
    assert payment.status_code == 201
    assert payment.get_json()["data"]["receipt_no"] == "RC-0001"
    plans = client.get(
        "/api/v1/fees/plans",
        headers={"Authorization": f"Bearer {admin}"},
    ).get_json()["data"]
    assert plans[0]["installments"][0]["status"] == "paid"


def test_overpayment_and_void_restore_balance(client, app):
    student_id = _student(app)
    admin = _token(client, "superadmin", "admin@example.com")
    plan = _plan(client, admin, student_id)
    installment_id = plan["installments"][0]["id"]
    over = client.post(
        "/api/v1/fees/payments",
        headers={"Authorization": f"Bearer {admin}"},
        json={"student_id": student_id, "installment_id": installment_id, "amount": 601},
    )
    assert over.status_code == 409
    payment = client.post(
        "/api/v1/fees/payments",
        headers={"Authorization": f"Bearer {admin}"},
        json={"student_id": student_id, "installment_id": installment_id, "amount": 100},
    )
    payment_id = payment.get_json()["data"]["id"]
    voided = client.post(
        f"/api/v1/fees/payments/{payment_id}/void",
        headers={"Authorization": f"Bearer {admin}"},
        json={"reason": "Duplicate entry"},
    )
    assert voided.status_code == 200
    assert voided.get_json()["data"]["status"] == "void"
    with app.app_context():
        installment = db.session.get(Installment, installment_id)
        assert installment.paid_amount == 0


def test_student_can_only_read_own_fees(client, app):
    student_id = _student(app)
    admin = _token(client, "superadmin", "admin@example.com")
    _plan(client, admin, student_id)
    student = _token(client, "student", "STU-FEE")
    response = client.get(
        "/api/v1/fees/me",
        headers={"Authorization": f"Bearer {student}"},
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["plans"][0]["student_id"] == student_id


def test_student_cannot_read_another_students_fees_or_receipt(client, app):
    first_student_id = _student(app)
    with app.app_context():
        user = User(
            email="other-fee-student@example.com",
            login_id="STU-FEE-OTHER",
            password_hash=generate_password_hash("password123"),
            role="student",
        )
        db.session.add(user)
        db.session.flush()
        other = Student(
            user_id=user.id,
            student_code="STU-FEE-OTHER",
            name="Other Fee Student",
            email=user.email,
        )
        db.session.add(other)
        db.session.commit()
        second_student_id = other.id

    admin = _token(client, "superadmin", "admin@example.com")
    first_plan = _plan(client, admin, first_student_id)
    second_plan = _plan(client, admin, second_student_id)
    payment = client.post(
        "/api/v1/fees/payments",
        headers={"Authorization": f"Bearer {admin}"},
        json={
            "student_id": second_student_id,
            "installment_id": second_plan["installments"][0]["id"],
            "amount": 600,
        },
    )
    assert payment.status_code == 201
    receipt_id = payment.get_json()["data"]["id"]

    student = _token(client, "student", "STU-FEE")
    fees = client.get("/api/v1/fees/me", headers={"Authorization": f"Bearer {student}"})
    assert fees.status_code == 200
    assert all(plan["student_id"] == first_student_id for plan in fees.get_json()["data"]["plans"])
    receipt = client.get(
        f"/api/v1/fees/payments/{receipt_id}/receipt",
        headers={"Authorization": f"Bearer {student}"},
    )
    assert receipt.status_code == 403


def test_receipts_are_unique_and_gap_free_for_concurrent_payments(tmp_path):
    class ConcurrentTestingConfig(TestingConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{Path(tmp_path) / 'concurrent.db'}"
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {"check_same_thread": False, "timeout": 30}
        }

    application = create_app(ConcurrentTestingConfig)
    with application.app_context():
        db.create_all()
        admin_user = User(
            email="concurrent-admin@example.com",
            login_id="concurrent-admin@example.com",
            password_hash=generate_password_hash("password123"),
            role="superadmin",
        )
        student_user = User(
            email="concurrent-student@example.com",
            login_id="CONCURRENT-STU",
            password_hash=generate_password_hash("password123"),
            role="student",
        )
        db.session.add_all([admin_user, student_user])
        db.session.flush()
        student = Student(
            user_id=student_user.id,
            student_code="CONCURRENT-STU",
            name="Concurrent Student",
        )
        db.session.add(student)
        db.session.commit()
        student_id = student.id

    setup_client = application.test_client()
    admin = _token(setup_client, "superadmin", "concurrent-admin@example.com", "password123")
    plan = _plan(setup_client, admin, student_id)
    installment_ids = [item["id"] for item in plan["installments"]]

    def pay(installment_id):
        with application.test_client() as worker:
            token = _token(worker, "superadmin", "concurrent-admin@example.com", "password123")
            response = worker.post(
                "/api/v1/fees/payments",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_id": student_id,
                    "installment_id": installment_id,
                    "amount": 200,
                },
            )
            return response.status_code, response.get_json()

    with ThreadPoolExecutor(max_workers=len(installment_ids)) as executor:
        results = list(executor.map(pay, installment_ids))

    assert [status for status, _ in results] == [201] * len(installment_ids)
    receipt_numbers = sorted(result["data"]["receipt_no"] for _, result in results)
    assert receipt_numbers == [f"RC-{number:04d}" for number in range(1, len(installment_ids) + 1)]
