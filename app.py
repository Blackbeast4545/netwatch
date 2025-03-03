import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import os

app = Flask(__name__, 
           template_folder='netwatch/templates',
           static_folder='netwatch/static')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret!')
app.config['DEBUG'] = False

# Initialize SocketIO with specific configuration
socketio = SocketIO(
    app,
    async_mode='eventlet',
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True) 