from app import db
from datetime import date

class Patient(db.Model):
    __tablename__ = 'patient'
    patient_id   = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False)
    dob          = db.Column(db.Date, nullable=False)
    join_date    = db.Column(db.Date, default=date.today)
    terminated   = db.Column(db.Boolean, nullable=True)
    termination_date = db.Column(db.Date, nullable=True)
    phone        = db.Column(db.String(20))
    address      = db.Column(db.String(255))
    parent_name  = db.Column(db.String(100))

    sessions = db.relationship('Session', back_populates='patient', lazy=True)
