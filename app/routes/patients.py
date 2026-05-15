from flask import Blueprint, request, jsonify
from app import db
from app.models.patient import Patient
from app.routes.decorators import login_required

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/patients', methods=['GET'])
#@login_required
def get_patients():
    patients = Patient.query.all()
    return jsonify([{
        'id': p.patient_id,
        'name': p.name,
        'dob': str(p.dob),
        'join_date': str(p.join_date),
        'terminated': p.terminated,
        'phone': p.phone,
        'address': p.address,
        'parent_name': p.parent_name
    } for p in patients])

@patients_bp.route('/patients/<int:id>', methods=['GET'])
@login_required
def get_patient(id):
    p = Patient.query.get_or_404(id)
    return jsonify({
        'id': p.patient_id,
        'name': p.name,
        'dob': str(p.dob),
        'join_date': str(p.join_date),
        'terminated': p.terminated,
        'phone': p.phone,
        'address': p.address,
        'parent_name': p.parent_name
    })

@patients_bp.route('/patients', methods=['POST'])
@login_required
def add_patient():
    data = request.get_json()
    patient = Patient(
        name=data.get('name'),
        dob=data.get('dob'),
        join_date=data.get('join_date'),
        terminated=data.get('terminated'),
        phone=data.get('phone'),
        address=data.get('address'),
        parent_name=data.get('parent_name')
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify({'message': 'Patient added', 'id': patient.patient_id}), 201

@patients_bp.route('/patients/<int:id>', methods=['PUT'])
@login_required
def update_patient(id):
    p = Patient.query.get_or_404(id)
    data = request.get_json()
    p.name = data.get('name', p.name)
    p.dob = data.get('dob', p.dob)
    p.join_date = data.get('join_date', p.join_date)
    p.terminated = data.get('terminated', p.terminated)
    p.phone = data.get('phone', p.phone)
    p.address = data.get('address', p.address)
    p.parent_name = data.get('parent_name', p.parent_name)
    db.session.commit()
    return jsonify({'message': 'Patient updated'})

@patients_bp.route('/patients/<int:id>', methods=['DELETE'])
@login_required
def delete_patient(id):
    p = Patient.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'Patient deleted'})