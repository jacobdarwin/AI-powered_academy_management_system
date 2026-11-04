from ..extensions import db


class ReceiptSequence(db.Model):
    __tablename__ = "receipt_sequences"
    id = db.Column(db.Integer, primary_key=True)
    prefix = db.Column(db.String(32), unique=True, nullable=False)
    next_number = db.Column(db.Integer, nullable=False, default=1)
