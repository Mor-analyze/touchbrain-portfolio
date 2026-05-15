from app import db, bcrypt
from datetime import date

class User(db.Model):
    __tablename__ = 'user'
    user_id       = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20), default='staff')  # 'admin' or 'staff'
    join_date     = db.Column(db.Date, default=date.today)
    active        = db.Column(db.Boolean, default=True)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)