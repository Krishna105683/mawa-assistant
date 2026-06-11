import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Use Supabase on server, SQLite locally
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL (Supabase) for server
    engine = create_engine(DATABASE_URL)
    USE_PG = True
else:
    # SQLite for local
    USE_PG = False

def init_db():
    if not USE_PG:
        from database import init_db as sqlite_init
        sqlite_init()
        return
    
    with engine.connect() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                task TEXT NOT NULL,
                due_time TEXT,
                done INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''))
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS reminders (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''))
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS habits (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''))
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS daily_routine (
                id SERIAL PRIMARY KEY,
                activity TEXT NOT NULL,
                time TEXT NOT NULL,
                active INTEGER DEFAULT 1
            )
        '''))
        conn.commit()
    print("PostgreSQL database ready!")

def add_task(task, due_time=None):
    if not USE_PG:
        from database import add_task as sqlite_add
        return sqlite_add(task, due_time)
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO tasks (task, due_time) VALUES (:task, :due_time)"),
                     {"task": task, "due_time": due_time})
        conn.commit()

def get_tasks():
    if not USE_PG:
        from database import get_tasks as sqlite_get
        return sqlite_get()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, task, due_time, done FROM tasks WHERE done = 0 ORDER BY created_at DESC"))
        return result.fetchall()

def complete_task(task_id):
    if not USE_PG:
        from database import complete_task as sqlite_complete
        return sqlite_complete(task_id)
    with engine.connect() as conn:
        conn.execute(text("UPDATE tasks SET done = 1 WHERE id = :id"), {"id": task_id})
        conn.commit()

def delete_task(task_id):
    if not USE_PG:
        from database import delete_task as sqlite_delete
        return sqlite_delete(task_id)
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM tasks WHERE id = :id"), {"id": task_id})
        conn.commit()

def add_reminder(title, remind_at):
    if not USE_PG:
        from database import add_reminder as sqlite_add
        return sqlite_add(title, remind_at)
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO reminders (title, remind_at) VALUES (:title, :remind_at)"),
                     {"title": title, "remind_at": remind_at})
        conn.commit()

def get_reminders():
    if not USE_PG:
        from database import get_reminders as sqlite_get
        return sqlite_get()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, title, remind_at, done FROM reminders WHERE done = 0 ORDER BY remind_at ASC"))
        return result.fetchall()

def add_habit(name):
    if not USE_PG:
        from routine import add_habit as sqlite_add
        return sqlite_add(name)
    from datetime import datetime
    import pytz
    IST = pytz.timezone('Asia/Kolkata')
    today = datetime.now(IST).strftime("%Y-%m-%d")
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO habits (name, date) VALUES (:name, :date)"),
                     {"name": name, "date": today})
        conn.commit()

def get_today_habits():
    if not USE_PG:
        from routine import get_today_habits as sqlite_get
        return sqlite_get()
    from datetime import datetime
    import pytz
    IST = pytz.timezone('Asia/Kolkata')
    today = datetime.now(IST).strftime("%Y-%m-%d")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name, completed FROM habits WHERE date = :date"),
                              {"date": today})
        return result.fetchall()

def complete_habit(habit_id):
    if not USE_PG:
        from routine import complete_habit as sqlite_complete
        return sqlite_complete(habit_id)
    with engine.connect() as conn:
        conn.execute(text("UPDATE habits SET completed = 1 WHERE id = :id"), {"id": habit_id})
        conn.commit()

def add_routine_activity(activity, time):
    if not USE_PG:
        from routine import add_routine_activity as sqlite_add
        return sqlite_add(activity, time)
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO daily_routine (activity, time) VALUES (:activity, :time)"),
                     {"activity": activity, "time": time})
        conn.commit()

def get_daily_routine():
    if not USE_PG:
        from routine import get_daily_routine as sqlite_get
        return sqlite_get()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, activity, time FROM daily_routine WHERE active = 1"))
        rows = result.fetchall()

    def sort_by_time(item):
        try:
            from datetime import datetime
            return datetime.strptime(item[2].strip().upper(), "%I:%M %p")
        except:
            return __import__('datetime').datetime.min

    return sorted(rows, key=sort_by_time)