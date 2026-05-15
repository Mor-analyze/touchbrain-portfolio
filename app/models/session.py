from app import db
from datetime import datetime

session_doctor = db.Table('session_doctor',
    db.Column('session_id', db.Integer, db.ForeignKey('session.session_id'), primary_key=True),
    db.Column('doctor_id',  db.Integer, db.ForeignKey('doctor.doctor_id'),  primary_key=True)
)

class Session(db.Model):
    __tablename__ = 'session'
    session_id   = db.Column(db.Integer, primary_key=True)
    patient_id   = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatment.treatment_id'), nullable=False)
    date_time    = db.Column(db.DateTime, default=datetime.utcnow)
    cost         = db.Column(db.Numeric(10, 2))
    discount     = db.Column(db.Numeric(10, 2), default=0)
    notes        = db.Column(db.Text)

    doctors   = db.relationship('Therapist', secondary=session_doctor, backref='sessions')
    patient   = db.relationship('Patient', back_populates='sessions')
    treatment = db.relationship('Treatment', backref='sessions')