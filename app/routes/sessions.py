from flask import Blueprint, request, jsonify
from app import db
from app.models.session import Session
from app.models.doctor import Therapist
from app.routes.decorators import login_required

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/sessions', methods=['GET'])
@login_required
def get_sessions():
    sessions = Session.query.all()
    return jsonify([{
        'id': s.session_id,
        'patient_id': s.patient_id,
        'treatment_id': s.treatment_id,
        'date_time': str(s.date_time),
        'cost': float(s.cost) if s.cost else None,
        'discount': float(s.discount) if s.discount else 0,
        'notes': s.notes,
        'therapists': [{'id': t.doctor_id, 'name': t.name} for t in s.doctors]
    } for s in sessions])

@sessions_bp.route('/sessions', methods=['POST'])
@login_required
def add_session():
    data = request.get_json()
    session = Session(
        patient_id=data.get('patient_id'),
        treatment_id=data.get('treatment_id'),
        date_time=data.get('date_time'),
        cost=data.get('cost'),
        discount=data.get('discount', 0),
        notes=data.get('notes')
    )
    therapist_ids = data.get('therapist_ids', [])
    for t_id in therapist_ids:
        therapist = Therapist.query.get(t_id)
        if therapist:
            session.doctors.append(therapist)
    db.session.add(session)
    db.session.commit()
    return jsonify({'message': 'Session added', 'id': session.session_id}), 201

@sessions_bp.route('/sessions/<int:id>', methods=['PUT'])
@login_required
def update_session(id):
    s = Session.query.get_or_404(id)
    data = request.get_json()
    s.patient_id = data.get('patient_id', s.patient_id)
    s.treatment_id = data.get('treatment_id', s.treatment_id)
    s.date_time = data.get('date_time', s.date_time)
    s.cost = data.get('cost', s.cost)
    s.discount = data.get('discount', s.discount)
    s.notes = data.get('notes', s.notes)
    if 'therapist_ids' in data:
        s.doctors = []
        for t_id in data['therapist_ids']:
            therapist = Therapist.query.get(t_id)
            if therapist:
                s.doctors.append(therapist)
        db.session.commit()
        return jsonify({'message': 'Session updated'})