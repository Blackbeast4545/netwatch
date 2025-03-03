import eventlet
eventlet.monkey_patch(socket=True, select=True)

from app import app, socketio

# Wrap the application with socketio middleware
application = socketio.middleware(app)

if __name__ == '__main__':
    socketio.run(app) 