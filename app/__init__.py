"""
Smart Crop Care Assistant - Flask Application Factory
"""

from flask import Flask, request, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_babel import Babel, get_locale
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
import tensorflow as tf
import json

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
babel = Babel()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"]
)

def load_ml_model(app):
    """Load the machine learning model and class indices."""
    app.ml_model = None
    app.ml_class_names = None
    try:
        model_path = app.config['ML_MODEL_PATH']
        class_indices_path = app.config['ML_CLASS_INDICES_PATH']

        if os.path.exists(model_path) and os.path.exists(class_indices_path):
            app.ml_model = tf.keras.models.load_model(model_path)
            with open(class_indices_path, 'r') as f:
                class_indices = json.load(f)
            # Convert keys to integers before creating the dictionary
            app.ml_class_names = {int(k): v for k, v in class_indices.items()}
            app.logger.info("Successfully loaded ML model and class indices.")
        else:
            app.logger.error(f"ML model not found at {model_path} or class indices not found at {class_indices_path}.")
            app.logger.error("Disease detection feature will be disabled.")
    except Exception as e:
        app.logger.error(f"An unexpected error occurred while loading the ML model: {e}", exc_info=True)
        app.logger.error("Disease detection feature will be disabled.")

def create_app(config_name='development'):
    """Application factory pattern."""
    
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Configure logging
    configure_logging(app)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    
    # Load ML model
    load_ml_model(app)
    
    # Configure Babel locale selector
    def get_locale():
        # 1. Check URL parameter for language switching
        if request.args.get('lang'):
            lang = request.args.get('lang')
            if lang in app.config.get('LANGUAGES', ['hi', 'en']):
                session['language'] = lang
                return lang
        
        # 2. Check user preference if logged in
        if current_user.is_authenticated and hasattr(current_user, 'preferred_language'):
            if current_user.preferred_language in app.config.get('LANGUAGES', ['hi', 'en']):
                return current_user.preferred_language
            
        # 3. Check session
        if 'language' in session:
            if session['language'] in app.config.get('LANGUAGES', ['hi', 'en']):
                return session['language']
        
        # 4. Check browser's Accept-Language header
        supported_languages = app.config.get('LANGUAGES', ['hi', 'en'])
        browser_language = request.accept_languages.best_match(supported_languages)
        if browser_language:
            return browser_language
            
        # 5. Default to Hindi (primary target audience)
        return 'hi'
    
    babel.init_app(app, locale_selector=get_locale)
    
    # Add Flask-Babel functions to template context
    @app.context_processor
    def inject_babel_functions():
        from flask_babel import _, ngettext, get_locale, lazy_gettext
        return dict(
            _=_,
            ngettext=ngettext,
            get_locale=get_locale,
            lazy_gettext=lazy_gettext
        )
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    
    # Use lazy_gettext for login message (evaluated at request time)
    from flask_babel import lazy_gettext as _l
    login_manager.login_message = _l('Please log in to access this page.')
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return db.session.get(User, int(user_id))
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        headers = app.config.get('SECURITY_HEADERS', {})
        for header, value in headers.items():
            response.headers[header] = value
        return response
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        g.start_time = datetime.now(timezone.utc)
        if app.config.get('DEBUG'):
            app.logger.debug(f'Request: {request.method} {request.url} from {request.remote_addr}')
    
    @app.after_request
    def log_response_info(response):
        if hasattr(g, 'start_time'):
            duration = (datetime.now(timezone.utc) - g.start_time).total_seconds()
            app.logger.info(f'{request.method} {request.url} - {response.status_code} - {duration:.3f}s')
        return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f'404 error for {request.url} from {request.remote_addr}')
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'500 error for {request.url} from {request.remote_addr}: {str(error)}')
        db.session.rollback()
        from flask import render_template
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning(f'Rate limit exceeded for {request.remote_addr}: {request.url}')
        from flask import render_template
        return render_template('errors/429.html'), 429
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.crops import crops_bp
    from app.routes.ai import ai_bp
    from app.routes.farms import farms_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(crops_bp, url_prefix='/crops')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(farms_bp, url_prefix='/farms')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

def configure_logging(app):
    """Configure application logging."""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Set up file handler with rotation
        file_handler = RotatingFileHandler(
            'logs/smart_agriculture.log', 
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Smart Crop Care Assistant application startup')
