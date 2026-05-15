from app import db
from datetime import date

class PaymentType(db.Model):
    __tablename__ = 'payment_type'
    payment_type_id = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(50), nullable=False)

class Payment(db.Model):
    __tablename__ = 'payment'
    payment_id      = db.Column(db.Integer, primary_key=True)
    session_id      = db.Column(db.Integer, db.ForeignKey('session.session_id'), nullable=False)
    payment_type_id = db.Column(db.Integer, db.ForeignKey('payment_type.payment_type_id'), nullable=False)
    amount          = db.Column(db.Numeric(10, 2), nullable=False)
    date            = db.Column(db.Date, default=date.today)

    payment_type = db.relationship('PaymentType', backref='payments')
