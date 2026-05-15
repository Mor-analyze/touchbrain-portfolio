from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from flask_jwt_extended import create_access_token
from app import bcrypt
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email'), active=True).first()
    if not user or not user.check_password(data.get('password')):
        return {'error': 'Invalid email or password'}, 401
    token = create_access_token(identity={
        'id': user.user_id,
        'name': user.name,
        'role': user.role
    })
    return {'token': token, 'role': user.role, 'name': user.name}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, active=True).first()
        if not user or not user.check_password(password):
            return render_template('login.html', error='Invalid email or password')
        session.permanent = True
        session['user_id'] = user.user_id
        session['user_name'] = user.name
        session['user_role'] = user.role
        return redirect(url_for('main.dashboard'))
    return render_template('login.html', error=None)

@auth_bp.route('/logout')
def logout_page():
    session.clear()
    response = redirect(url_for('auth.login_page'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response