from app.auth import init_db
from werkzeug.security import generate_password_hash
import sqlite3

def create_admin_user():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    # Create admin user
    username = 'admin'
    password = 'admin123'  # Change this to your desired password
    password_hash = generate_password_hash(password)
    
    try:
        cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                   (username, password_hash))
        conn.commit()
        print("Admin user created successfully!")
    except sqlite3.IntegrityError:
        print("Admin user already exists!")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    create_admin_user() 