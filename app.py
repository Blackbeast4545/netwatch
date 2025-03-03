import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__, 
           template_folder='netwatch/templates',
           static_folder='netwatch/static')
app.config['SECRET_KEY'] = 'secret!'

# Initialize SocketIO with specific configuration
socketio = SocketIO(app, 
                   async_mode='eventlet',
                   cors_allowed_origins="*",
                   engineio_logger=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    socketio.run(app, debug=True) 