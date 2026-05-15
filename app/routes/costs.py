from flask import Blueprint, request, jsonify
from app import db
from app.models.cost import Cost, CostCategory
from app.routes.decorators import login_required, admin_required

costs_bp = Blueprint('costs', __name__)

@costs_bp.route('/costs', methods=['GET'])
@login_required
def get_costs():
    costs = Cost.query.all()
    return jsonify([{
        'id': c.cost_id,
        'category_id': c.cost_category_id,
        'amount': float(c.amount),
        'date': str(c.date),
        'description': c.description
    } for c in costs])

@costs_bp.route('/costs', methods=['POST'])
@admin_required
def add_cost():
    data = request.get_json()
    cost = Cost(
        cost_category_id=data.get('cost_category_id'),
        amount=data.get('amount'),
        date=data.get('date'),
        description=data.get('description')
    )
    db.session.add(cost)
    db.session.commit()
    return jsonify({'message': 'Cost added', 'id': cost.cost_id}), 201

@costs_bp.route('/cost-categories', methods=['GET'])
@login_required
def get_cost_categories():
    cats = CostCategory.query.all()
    return jsonify([{'id': c.cost_category_id, 'name': c.name} for c in cats])