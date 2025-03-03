from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager

socketio = SocketIO()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    # For now, return None as we haven't implemented user management yet
    return None

def create_app(debug=False):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    app.config['DEBUG'] = debug

    login_manager.init_app(app)
    login_manager.login_view = 'main.index'

    socketio.init_app(app)

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app 