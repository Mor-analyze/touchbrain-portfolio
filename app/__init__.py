from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        from app.models.patient import Patient
        from app.models.doctor import Therapist
        from app.models.treatment import Treatment
        from app.models.session import Session, session_doctor
        from app.models.assessment import Assessment
        from app.models.cost import CostCategory, Cost
        from app.models.user import User

        from app.routes.auth import auth_bp
        from app.routes.patients import patients_bp
        from app.routes.doctors import doctors_bp
        from app.routes.sessions import sessions_bp
        from app.routes.costs import costs_bp
        from app.routes.main import main_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(patients_bp, url_prefix='/api')
        app.register_blueprint(doctors_bp, url_prefix='/api')
        app.register_blueprint(sessions_bp, url_prefix='/api')
        app.register_blueprint(costs_bp, url_prefix='/api')
        app.register_blueprint(main_bp)

    return app