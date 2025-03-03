from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager

socketio = SocketIO()
login_manager = LoginManager()

def create_app(debug=False):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    app.config['DEBUG'] = debug

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    login_manager.init_app(app)
    socketio.init_app(app)

    return app 