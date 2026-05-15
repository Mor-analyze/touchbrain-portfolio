from app import db
from datetime import date

class Assessment(db.Model):
    __tablename__ = 'assessment'
    assessment_id = db.Column(db.Integer, primary_key=True)
    patient_id    = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    type          = db.Column(db.String(20), nullable=False)  # 'brainmap' or 'remap'
    date          = db.Column(db.Date, default=date.today)
    notes         = db.Column(db.Text, nullable=True)

    patient = db.relationship('Patient', backref='assessments')