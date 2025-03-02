from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
import os
import logging
from logging.handlers import RotatingFileHandler

socketio = SocketIO(cors_allowed_origins="*")
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '1234567891')
    
    # Configure for production
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['REMEMBER_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from .routes import main
    from .auth import auth, init_db
    app.register_blueprint(main)
    app.register_blueprint(auth)
    
    # Initialize SocketIO
    socketio.init_app(app, 
                     async_mode='threading',
                     cors_allowed_origins="*",
                     ping_timeout=5,
                     ping_interval=25)
    
    # Initialize the database
    init_db()
    
    if os.environ.get('FLASK_ENV') == 'production':
        # Configure logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/netwatch.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('NetWatch startup')
    
    return app 