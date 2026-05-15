from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models.doctor import Therapist
from app.routes.decorators import login_required
from datetime import date

doctors_bp = Blueprint('doctors', __name__)

@doctors_bp.route('/therapists', methods=['GET'])
@login_required
def get_therapists():
    therapists = Therapist.query.all()
    return jsonify([{
        'id': t.doctor_id,
        'name': t.name,
        'phone': t.phone,
        'email': t.email,
        'join_date': str(t.join_date),
        'termination_date': str(t.termination_date) if t.termination_date else None
    } for t in therapists])

@doctors_bp.route('/therapists', methods=['POST'])
@login_required
def add_therapist():
    data = request.get_json()
    therapist = Therapist(
        name=data.get('name'),
        phone=data.get('phone'),
        email=data.get('email'),
        password_hash=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='admin',
        join_date=data.get('join_date', date.today())
    )
    db.session.add(therapist)
    db.session.commit()
    return jsonify({'message': 'Therapist added', 'id': therapist.doctor_id}), 201

@doctors_bp.route('/therapists/<int:id>', methods=['PUT'])
@login_required
def update_therapist(id):
    t = Therapist.query.get_or_404(id)
    data = request.get_json()
    t.name = data.get('name', t.name)
    t.phone = data.get('phone', t.phone)
    t.email = data.get('email', t.email)
    if data.get('termination_date'):
        t.termination_date = data.get('termination_date')
    db.session.commit()
    return jsonify({'message': 'Therapist updated'})

@doctors_bp.route('/therapists/<int:id>', methods=['DELETE'])
@login_required
def delete_therapist(id):
    t = Therapist.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({'message': 'Therapist deleted'})