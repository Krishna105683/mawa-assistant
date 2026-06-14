import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
USE_PG = bool(DATABASE_URL)

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    if not USE_PG:
        from database import init_db as sqlite_init
        sqlite_init()
        return
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY, task TEXT NOT NULL,
        due_time TEXT, done INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS reminders (
        id SERIAL PRIMARY KEY, title TEXT NOT NULL,
        remind_at TEXT NOT NULL, done INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS habits (
        id SERIAL PRIMARY KEY, name TEXT NOT NULL,
        completed INTEGER DEFAULT 0, date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS daily_routine (
        id SERIAL PRIMARY KEY, activity TEXT NOT NULL,
        time TEXT NOT NULL, active INTEGER DEFAULT 1)''')
    conn.commit()
    cur.close()
    conn.close()
    print("PostgreSQL database ready!")

def add_task(task, due_time=None):
    if not USE_PG:
        from database import add_task as f; return f(task, due_time)
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO tasks (task, due_time) VALUES (%s, %s)", (task, due_time))
    conn.commit(); cur.close(); conn.close()

def get_tasks():
    if not USE_PG:
        from database import get_tasks as f; return f()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, task, due_time, done FROM tasks WHERE done = 0 ORDER BY created_at DESC")
    rows = cur.fetchall(); cur.close(); conn.close(); return rows

def complete_task(task_id):
    if not USE_PG:
        from database import complete_task as f; return f(task_id)
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE tasks SET done = 1 WHERE id = %s", (task_id,))
    conn.commit(); cur.close(); conn.close()

def delete_task(task_id):
    if not USE_PG:
        from database import delete_task as f; return f(task_id)
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit(); cur.close(); conn.close()

def add_reminder(title, remind_at):
    if not USE_PG:
        from database import add_reminder as f; return f(title, remind_at)
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO reminders (title, remind_at) VALUES (%s, %s)", (title, remind_at))
    conn.commit(); cur.close(); conn.close()

def get_reminders():
    if not USE_PG:
        from database import get_reminders as f; return f()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, title, remind_at, done FROM reminders WHERE done = 0 ORDER BY remind_at ASC")
    rows = cur.fetchall(); cur.close(); conn.close(); return rows

def add_habit(name):
    if not USE_PG:
        from routine import add_habit as f; return f(name)
    IST = pytz.timezone('Asia/Kolkata')
    today = datetime.now(IST).strftime("%Y-%m-%d")
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO habits (name, date) VALUES (%s, %s)", (name, today))
    conn.commit(); cur.close(); conn.close()

def get_today_habits():
    if not USE_PG:
        from routine import get_today_habits as f; return f()
    IST = pytz.timezone('Asia/Kolkata')
    today = datetime.now(IST).strftime("%Y-%m-%d")
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, name, completed FROM habits WHERE date = %s", (today,))
    rows = cur.fetchall(); cur.close(); conn.close(); return rows

def complete_habit(habit_id):
    if not USE_PG:
        from routine import complete_habit as f; return f(habit_id)
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE habits SET completed = 1 WHERE id = %s", (habit_id,))
    conn.commit(); cur.close(); conn.close()

def add_routine_activity(activity, time):
    if not USE_PG:
        from routine import add_routine_activity as f; return f(activity, time)
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO daily_routine (activity, time) VALUES (%s, %s)", (activity, time))
    conn.commit(); cur.close(); conn.close()

def get_daily_routine():
    if not USE_PG:
        from routine import get_daily_routine as f; return f()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, activity, time FROM daily_routine WHERE active = 1")
    rows = cur.fetchall(); cur.close(); conn.close()
    def sort_by_time(item):
        try: return datetime.strptime(item[2].strip().upper(), "%I:%M %p")
        except: return datetime.min
    return sorted(rows, key=sort_by_time)