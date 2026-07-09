import bcrypt
import sqlite3
import os
from datetime import datetime
import pytz

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'nova.db')

if os.environ.get('RENDER'):
    DB_PATH = '/tmp/nova.db'

def init_users_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            language TEXT DEFAULT 'english',
            setup_done INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Users table ready!")

def register_user(name, email, password):
    try:
        # Hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed.decode('utf-8'))
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"success": True, "user_id": user_id, "name": name}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "Email already registered!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def login_user(email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, password, language, setup_done FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return {"success": False, "error": "Email not found!"}
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            return {
                "success": True,
                "user_id": user[0],
                "name": user[1],
                "email": user[2],
                "language": user[4],
                "setup_done": user[5]
            }
        else:
            return {"success": False, "error": "Wrong password!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def complete_setup(user_id, language):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET setup_done = 1, language = ? WHERE id = ?",
        (language, user_id)
    )
    conn.commit()
    conn.close()
    