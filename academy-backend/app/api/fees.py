from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, g, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ..auth import authenticated, roles_required
from ..extensions import db
from ..models import Expense, FeePlan, Installment, Payment, ReceiptSequence, Student
from ..responses import failure, success

fees_api = Blueprint("fees", __name__, url_prefix="/fees")


def _date(value):
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _money(value):
    try:
        amount = Decimal(str(value))
        return amount if amount >= 0 else None
    except (InvalidOperation, TypeError, ValueError):
        return None


def _student_for_user():
    return db.session.scalar(db.select(Student).where(Student.user_id == g.current_user_id))


def _plan(item: FeePlan) -> dict:
    installments = db.session.scalars(
        db.select(Installment).where(Installment.fee_plan_id == item.id).order_by(Installment.due_date)
    ).all()
    return {
        "id": item.id,
        "student_id": item.student_id,
        "final_amount": str(item.final_amount),
        "status": item.status,
        "installments": [_installment(installment) for installment in installments],
    }


def _installment(item: Installment) -> dict:
    return {
        "id": item.id,
        "fee_plan_id": item.fee_plan_id,
        "label": item.label,
        "due_date": item.due_date.isoformat(),
        "amount": str(item.amount),
        "paid_amount": str(item.paid_amount),
        "status": item.status,
    }


def _payment(item: Payment) -> dict:
    return {
        "id": item.id,
        "student_id": item.student_id,
        "installment_id": item.installment_id,
        "receipt_no": item.receipt_no,
        "amount": str(item.amount),
        "mode": item.mode,
        "reference": item.reference,
        "status": item.status,
        "created_at": item.created_at.isoformat(),
    }


def _expense(item: Expense) -> dict:
    return {
        "id": item.id, "category": item.category, "amount": str(item.amount),
        "note": item.note, "date": item.date.isoformat(),
    }


def _refresh_status(installment: Installment):
    if installment.paid_amount >= installment.amount:
        installment.status = "paid"
    elif installment.paid_amount > 0:
        installment.status = "partial"
    elif installment.due_date < date.today():
        installment.status = "overdue"
    else:
        installment.status = "pending"


def _next_receipt(prefix: str) -> str:
    sequence = db.session.scalar(
        db.select(ReceiptSequence).where(ReceiptSequence.prefix == prefix).with_for_update()
    )
    if sequence is None:
        try:
            with db.session.begin_nested():
                db.session.add(ReceiptSequence(prefix=prefix, next_number=2))
                db.session.flush()
            number = 1
        except IntegrityError:
            sequence = db.session.scalar(
                db.select(ReceiptSequence).where(ReceiptSequence.prefix == prefix).with_for_update()
            )
            number = sequence.next_number
            sequence.next_number += 1
    else:
        number = sequence.next_number
        sequence.next_number += 1
    return f"{prefix}-{number:04d}"


@fees_api.post("/plans")
@roles_required("superadmin", "staff")
def create_plan():
    if g.current_claims.get("role") == "staff" and g.current_claims.get("designation") != "accounts":
        return failure("Forbidden", 403)
    body = request.get_json(silent=True) or {}
    student_id = body.get("student_id")
    final_amount = _money(body.get("final_amount"))
    installments = body.get("installments")
    if (
        not isinstance(student_id, int)
        or not db.session.get(Student, student_id)
        or final_amount is None
        or final_amount <= 0
        or not isinstance(installments, list)
        or not installments
    ):
        return failure("Validation failed", 422, {"fee_plan": ["Student, amount, and installments are required."]})
    parsed = []
    for item in installments:
        amount = _money(item.get("amount"))
        due_date = _date(item.get("due_date"))
        label = str(item.get("label", "")).strip()
        if not label or amount is None or amount <= 0 or due_date is None:
            return failure("Validation failed", 422, {"installments": ["Each installment needs label, date, and amount."]})
        parsed.append((label, due_date, amount))
    if sum(amount for _, _, amount in parsed) != final_amount:
        return failure("Installments must sum to final_amount", 422)
    plan = FeePlan(student_id=student_id, final_amount=final_amount)
    db.session.add(plan)
    db.session.flush()
    db.session.add_all(
        [
            Installment(fee_plan_id=plan.id, label=label, due_date=due_date, amount=amount)
            for label, due_date, amount in parsed
        ]
    )
    db.session.commit()
    return success(_plan(plan), "Fee plan created", 201)


@fees_api.get("/plans")
@roles_required("superadmin", "staff")
def list_plans():
    if g.current_claims.get("role") == "staff" and g.current_claims.get("designation") != "accounts":
        return failure("Forbidden", 403)
    statement = db.select(FeePlan).order_by(FeePlan.id.desc())
    if request.args.get("student_id", type=int):
        statement = statement.where(FeePlan.student_id == request.args["student_id"])
    return success([_plan(item) for item in db.session.scalars(statement)])


@fees_api.post("/payments")
@roles_required("superadmin", "staff")
def create_payment():
    if g.current_claims.get("role") == "staff" and g.current_claims.get("designation") != "accounts":
        return failure("Forbidden", 403)
    body = request.get_json(silent=True) or {}
    student_id = body.get("student_id")
    amount = _money(body.get("amount"))
    if not isinstance(student_id, int) or amount is None or amount <= 0:
        return failure("Validation failed", 422, {"payment": ["Student and positive amount are required."]})
    student = db.session.get(Student, student_id)
    if not student:
        return failure("Student not found", 404)
    installment_id = body.get("installment_id")
    if installment_id:
        installment = db.session.scalar(
            db.select(Installment).join(FeePlan).where(
                Installment.id == installment_id, FeePlan.student_id == student_id
            )
        )
        if not installment:
            return failure("Installment not found", 404)
        remaining = installment.amount - installment.paid_amount
        if amount > remaining:
            return failure("Payment exceeds installment balance", 409)
    else:
        installment = None
        remaining = None
        installments = db.session.scalars(
            db.select(Installment)
            .join(FeePlan)
            .where(FeePlan.student_id == student_id, Installment.status != "paid")
            .order_by(Installment.due_date, Installment.id)
        ).all()
        if amount > sum(item.amount - item.paid_amount for item in installments):
            return failure("Payment exceeds outstanding balance", 409)
    try:
        receipt = _next_receipt("RC")
        payment = Payment(
            student_id=student_id,
            installment_id=installment.id if installment else None,
            receipt_no=receipt,
            amount=amount,
            mode=str(body.get("mode", "cash")).strip(),
            reference=str(body.get("reference", "")).strip() or None,
        )
        db.session.add(payment)
        if installment:
            installment.paid_amount += amount
            _refresh_status(installment)
        else:
            remaining_payment = amount
            for item in installments:
                allocation = min(remaining_payment, item.amount - item.paid_amount)
                item.paid_amount += allocation
                remaining_payment -= allocation
                _refresh_status(item)
                if remaining_payment == 0:
                    break
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("Payment could not be recorded", 409)
    return success(_payment(payment), "Payment recorded", 201)


@fees_api.get("/payments")
@roles_required("superadmin", "staff")
def list_payments():
    if g.current_claims.get("role") == "staff" and g.current_claims.get("designation") != "accounts":
        return failure("Forbidden", 403)
    statement = db.select(Payment).order_by(Payment.created_at.desc())
    if request.args.get("student_id", type=int):
        statement = statement.where(Payment.student_id == request.args["student_id"])
    return success([_payment(item) for item in db.session.scalars(statement)])


@fees_api.post("/payments/<int:payment_id>/void")
@roles_required("superadmin", "staff")
def void_payment(payment_id: int):
    if g.current_claims.get("role") == "staff" and g.current_claims.get("designation") != "accounts":
        return failure("Forbidden", 403)
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return failure("Payment not found", 404)
    if payment.status == "void":
        return failure("Payment is already void", 409)
    reason = str((request.get_json(silent=True) or {}).get("reason", "")).strip()
    if not reason:
        return failure("Validation failed", 422, {"reason": ["A void reason is required."]})
    if payment.installment_id:
        installment = db.session.get(Installment, payment.installment_id)
        installment.paid_amount -= payment.amount
        _refresh_status(installment)
    payment.status = "void"
    payment.void_reason = reason
    db.session.commit()
    return success(_payment(payment), "Payment voided")


@fees_api.get("/payments/<int:payment_id>/receipt")
@authenticated
def payment_receipt(payment_id: int):
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return failure("Payment not found", 404)
    student = _student_for_user()
    if g.current_claims.get("role") == "student" and (not student or student.id != payment.student_id):
        return failure("Forbidden", 403)
    return success(_payment(payment))


@fees_api.get("/dues")
@roles_required("superadmin", "staff")
def dues():
    if g.current_claims.get("role") == "staff" and g.current_claims.get("designation") != "accounts":
        return failure("Forbidden", 403)
    installments = db.session.scalars(
        db.select(Installment).where(Installment.status.in_(["pending", "partial", "overdue"]))
    ).all()
    return success([_installment(item) for item in installments])


@fees_api.route("/expenses", methods=["GET", "POST"])
@roles_required("superadmin", "staff")
def expenses():
    if g.current_claims.get("role") == "staff" and g.current_claims.get("designation") != "accounts":
        return failure("Forbidden", 403)
    if request.method == "GET":
        statement = db.select(Expense).order_by(Expense.date.desc(), Expense.id.desc())
        return success([_expense(item) for item in db.session.scalars(statement)])
    body = request.get_json(silent=True) or {}
    amount = _money(body.get("amount"))
    expense_date = _date(body.get("date"))
    category = str(body.get("category", "")).strip()
    if not category or amount is None or amount <= 0 or expense_date is None:
        return failure("Validation failed", 422, {
            "category": ["Category is required."] if not category else [],
            "amount": ["Enter a positive amount."] if amount is None or amount <= 0 else [],
            "date": ["Use YYYY-MM-DD."] if expense_date is None else [],
        })
    item = Expense(category=category, amount=amount, note=str(body.get("note", "")).strip() or None,
                   date=expense_date, created_by=g.current_user_id)
    db.session.add(item)
    db.session.commit()
    return success(_expense(item), "Expense recorded", 201)


@fees_api.patch("/expenses/<int:expense_id>")
@roles_required("superadmin", "staff")
def update_expense(expense_id):
    item = db.session.get(Expense, expense_id)
    if not item:
        return failure("Expense not found", 404)
    body = request.get_json(silent=True) or {}
    if "category" in body and str(body["category"]).strip():
        item.category = str(body["category"]).strip()
    if "note" in body:
        item.note = str(body["note"]).strip() or None
    if "amount" in body:
        amount = _money(body["amount"])
        if amount is None or amount <= 0:
            return failure("Validation failed", 422, {"amount": ["Enter a positive amount."]})
        item.amount = amount
    if "date" in body:
        parsed = _date(body["date"])
        if parsed is None:
            return failure("Validation failed", 422, {"date": ["Use YYYY-MM-DD."]})
        item.date = parsed
    db.session.commit()
    return success(_expense(item))


@fees_api.get("/me")
@roles_required("student")
def my_fees():
    student = _student_for_user()
    if not student:
        return failure("Student profile not found", 404)
    plans = db.session.scalars(db.select(FeePlan).where(FeePlan.student_id == student.id)).all()
    payments = db.session.scalars(db.select(Payment).where(Payment.student_id == student.id)).all()
    return success({"plans": [_plan(item) for item in plans], "payments": [_payment(item) for item in payments]})
