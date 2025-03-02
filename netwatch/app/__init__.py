from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager

socketio = SocketIO(cors_allowed_origins="*")  # Allow all origins for development
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '1234567891'
    app.config['DEBUG'] = False  # Disable debug mode
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    # Disable Flask logging
    app.logger.disabled = True
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from .routes import main
    from .auth import auth, init_db
    app.register_blueprint(main)
    app.register_blueprint(auth)
    
    # Initialize SocketIO with minimal logging
    socketio.init_app(app, 
                     async_mode='threading',
                     cors_allowed_origins="*",
                     ping_timeout=5,
                     ping_interval=25,
                     logger=False,  # Disable SocketIO logging
                     engineio_logger=False)  # Disable Engine.IO logging
    
    # Initialize the database
    init_db()

    # Minimal error handling
    @app.errorhandler(Exception)
    def handle_error(error):
        return str(error), 500
    
    return app 