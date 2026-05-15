from app import db
from datetime import date

class CostCategory(db.Model):
    __tablename__ = 'cost_category'
    cost_category_id = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(100), nullable=False)

class Cost(db.Model):
    __tablename__ = 'cost'
    cost_id          = db.Column(db.Integer, primary_key=True)
    cost_category_id = db.Column(db.Integer, db.ForeignKey('cost_category.cost_category_id'), nullable=False)
    amount           = db.Column(db.Numeric(10, 2), nullable=False)
    date             = db.Column(db.Date, default=date.today)
    description      = db.Column(db.String(255))

    category = db.relationship('CostCategory', backref='costs')
