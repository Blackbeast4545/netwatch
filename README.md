# NetWatch - Network Monitoring Tool

A real-time network monitoring tool built with Flask and SocketIO.

## Features
- Real-time network monitoring
- Dashboard interface
- WebSocket support for live updates
- Network statistics tracking

## Local Development
1. Clone the repository:
```bash
git clone https://github.com/yourusername/netwatch.git
cd netwatch
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

## Deployment
The application is automatically deployed using GitHub Actions.
Visit: https://yourusername.github.io/netwatch/

## Environment Variables
- `SECRET_KEY`: Application secret key
- `FLASK_ENV`: Application environment (development/production)
- `DEBUG`: Debug mode (True/False)

## Tech Stack
- Flask
- Flask-SocketIO
- Eventlet
- Python 3.11
- HTML/CSS
- WebSocket 