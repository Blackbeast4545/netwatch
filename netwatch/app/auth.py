from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from . import login_manager

auth = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cur.fetchone()
        conn.close()
        if not user:
            return None
        return User(user[0], user[1])

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         username TEXT UNIQUE NOT NULL,
         password_hash TEXT NOT NULL)
    ''')
    
    # Create default admin user if not exists
    cur.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cur.fetchone():
        cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                   ('admin', generate_password_hash('admin123')))
    
    conn.commit()
    conn.close()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1])
            login_user(user_obj)
            return redirect(url_for('main.dashboard'))
        
        flash('Please check your login details and try again.')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 