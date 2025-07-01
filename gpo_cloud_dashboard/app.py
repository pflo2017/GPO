import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g, request, session
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from .models import db, User
from .auth import auth_bp
from .main import main_bp
from .config import config


def create_app(config_name='default'):
    """Create Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize login manager
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # Setup logging
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configure file handler
        file_handler = RotatingFileHandler(
            'logs/gpo.log', 
            maxBytes=10240, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        # Add handler to app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.info('GPO Central Intelligence Dashboard startup')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'development')
    app.run(host='0.0.0.0', port=5000, debug=True) 