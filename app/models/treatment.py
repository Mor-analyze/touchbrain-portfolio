from app import db

class Treatment(db.Model):
    __tablename__ = 'treatment'
    treatment_id = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False)