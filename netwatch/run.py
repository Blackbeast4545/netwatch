from app import create_app
from os import environ
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == '__main__':
    port = int(environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 