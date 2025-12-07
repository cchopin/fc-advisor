"""
FC-Advisor: Fleet Commander Rating Application
A fun and humorous way to celebrate Eve Online Fleet Commanders
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    """Application factory pattern"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'fc_advisor.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=True,
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    # Import and register blueprints
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.webhook import webhook_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(webhook_bp, url_prefix='/webhook')
    
    # Create database tables
    with app.app_context():
        from app import models
        db.create_all()
        
        # Initialize default tags
        from app.tags import init_default_tags
        init_default_tags()
    
    return app


# CLI command to create admin
def create_admin_cli():
    """Create an admin user from command line"""
    import sys
    from werkzeug.security import generate_password_hash
    
    app = create_app()
    with app.app_context():
        from app.models import Admin
        
        if len(sys.argv) != 3:
            print("Usage: python -m app.create_admin <username> <password>")
            sys.exit(1)
        
        username = sys.argv[1]
        password = sys.argv[2]
        
        if Admin.query.filter_by(username=username).first():
            print(f"User '{username}' already exists!")
            sys.exit(1)
        
        admin = Admin(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin '{username}' created successfully!")
