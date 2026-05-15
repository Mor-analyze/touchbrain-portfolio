from flask import Blueprint, request, jsonify
from app import db
from app.models.payment import Payment, PaymentType
from app.routes.decorators import login_required

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/payments', methods=['GET'])
@login_required
def get_payments():
    payments = Payment.query.all()
    return jsonify([{
        'id': p.payment_id,
        'session_id': p.session_id,
        'payment_type_id': p.payment_type_id,
        'amount': float(p.amount),
        'date': str(p.date)
    } for p in payments])

@payments_bp.route('/payments', methods=['POST'])
@login_required
def add_payment():
    data = request.get_json()
    payment = Payment(
        session_id=data.get('session_id'),
        payment_type_id=data.get('payment_type_id'),
        amount=data.get('amount'),
        date=data.get('date')
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({'message': 'Payment recorded', 'id': payment.payment_id}), 201

@payments_bp.route('/payment-types', methods=['GET'])
@login_required
def get_payment_types():
    types = PaymentType.query.all()
    return jsonify([{'id': t.payment_type_id, 'name': t.name} for t in types])