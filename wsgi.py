from netwatch import create_app, socketio

application = create_app()
app = application

if __name__ == "__main__":
    socketio.run(application) 