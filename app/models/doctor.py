from app import db
from datetime import date

class Therapist(db.Model):
    __tablename__ = 'doctor'
    doctor_id        = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(100), nullable=False)
    phone            = db.Column(db.String(20))
    email            = db.Column(db.String(120), nullable=True)
    password_hash    = db.Column(db.String(255), nullable=False)
    role             = db.Column(db.String(20), default='doctor')
    join_date        = db.Column(db.Date, default=date.today)
    termination_date = db.Column(db.Date, nullable=True)