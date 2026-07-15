import sqlite3
import os

import sys
if 'render' in os.environ.get('RENDER', '').lower() or os.environ.get('RENDER'):
    DB_PATH = '/tmp/nova.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'nova.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tasks table with time period
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            due_time TEXT DEFAULT NULL,
            done INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Reminders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            remind_at TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def add_task(task, due_time=None, user_id=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task, due_time) VALUES (?, ?)", (task, due_time))
    conn.commit()
    conn.close()

def get_tasks(user_id=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, due_time, done FROM tasks WHERE done = 0 ORDER BY created_at DESC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def complete_task(task_id, user_id=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def delete_task(task_id, user_id=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def add_reminder(title, remind_at, user_id=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (title, remind_at) VALUES (?, ?)", (title, remind_at))
    conn.commit()
    conn.close()

def get_reminders(user_id=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, remind_at, done FROM reminders WHERE done = 0 ORDER BY remind_at ASC")
    reminders = cursor.fetchall()
    conn.close()
    return reminders