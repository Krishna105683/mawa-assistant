import os
from datetime import datetime, timedelta
import sqlite3
import re

if os.environ.get('RENDER'):
    DB_PATH = '/tmp/nova.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'nova.db')

def init_routine_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_routine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity TEXT NOT NULL,
            time TEXT NOT NULL,
            active INTEGER DEFAULT 1
        )
    ''')

    conn.commit()
    conn.close()

def add_habit(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO habits (name, date) VALUES (?, ?)", (name, today))
    conn.commit()
    conn.close()

def get_today_habits():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT id, name, completed FROM habits WHERE date = ?", (today,))
    habits = cursor.fetchall()
    conn.close()
    return habits

def complete_habit(habit_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE habits SET completed = 1 WHERE id = ?", (habit_id,))
    conn.commit()
    conn.close()

def get_habit_streak(habit_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, completed FROM habits 
        WHERE name = ? 
        ORDER BY date DESC 
        LIMIT 30
    """, (habit_name,))
    records = cursor.fetchall()
    conn.close()

    streak = 0
    for record in records:
        if record[1] == 1:
            streak += 1
        else:
            break
    return streak

def add_routine_activity(activity, time):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO daily_routine (activity, time) VALUES (?, ?)",
                   (activity, time))
    conn.commit()
    conn.close()

def get_daily_routine():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, activity, time FROM daily_routine WHERE active = 1")
    routine = cursor.fetchall()
    conn.close()

    def sort_by_time(item):
        try:
            return datetime.strptime(item[2].strip().upper(), "%I:%M %p")
        except:
            try:
                return datetime.strptime(item[2].strip(), "%H:%M")
            except:
                return datetime.min

    return sorted(routine, key=sort_by_time)

def get_morning_briefing(weather_func, tasks_func, reminders_func):
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    hour = now.hour

    if hour < 12:
        greeting = "Suprabhat"
    elif hour < 17:
        greeting = "Namaskar"
    else:
        greeting = "Shubh Sandhya"

    tasks = tasks_func()
    reminders = reminders_func()
    routine = get_daily_routine()
    habits = get_today_habits()

    briefing = f"{greeting} Krishna! Aaj {now.strftime('%A, %d %B %Y')} hai. "

    # Tasks with names
    if tasks:
        briefing += f"Aapke {len(tasks)} pending tasks hain: "
        for t in tasks:
            time_info = f" at {t[2]}" if t[2] else ""
            briefing += f"{t[1]}{time_info}, "
        briefing = briefing.rstrip(", ") + ". "
    else:
        briefing += "Aaj koi pending task nahi hai. "

    # Reminders with names
    if reminders:
        briefing += f"Aapke {len(reminders)} reminders hain: "
        for r in reminders:
            try:
                # Convert datetime string to readable time
                r_time = datetime.strptime(r[2], "%Y-%m-%d %H:%M:%S")
                time_str = r_time.strftime("%I:%M %p")
            except:
                time_str = r[2]
            briefing += f"{r[1]} at {time_str}, "
        briefing = briefing.rstrip(", ") + ". "

    # Next routine activity
    if routine:
        next_activity = None
        for r in routine:
            try:
                r_time = datetime.strptime(r[2].strip().upper(), "%I:%M %p")
                r_time = now.replace(hour=r_time.hour, minute=r_time.minute)
                if r_time > now:
                    next_activity = r
                    break
            except:
                pass
        if next_activity:
            briefing += f"Agla routine: {next_activity[1]} at {next_activity[2]}. "

    # Habits with names
    completed_habits = [h for h in habits if h[2] == 1]
    pending_habits = [h for h in habits if h[2] == 0]

    if habits:
        briefing += f"Aaj {len(completed_habits)} out of {len(habits)} habits complete ki hain. "
        if completed_habits:
            completed_names = ", ".join([h[1] for h in completed_habits])
            briefing += f"Complete: {completed_names}. "
        if pending_habits:
            pending_names = ", ".join([h[1] for h in pending_habits])
            briefing += f"Pending habits: {pending_names}. "

    briefing += "Batao kya madad chahiye?"
    return briefing

def get_weekly_review():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT COUNT(*) FROM tasks 
        WHERE done = 1 
        AND created_at >= ?
    """, (week_ago,))
    tasks_done = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM habits 
        WHERE completed = 1 
        AND date >= ?
    """, (week_ago,))
    habits_done = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM habits 
        WHERE date >= ?
    """, (week_ago,))
    total_habits = cursor.fetchone()[0]

    conn.close()

    review = "Is hafte ka review Krishna! "
    review += f"Aapne {tasks_done} tasks complete kiye. "

    if total_habits > 0:
        habit_pct = int((habits_done / total_habits) * 100)
        review += f"Aur {habit_pct}% habits follow ki. "

        if habit_pct >= 80:
            review += "Bahut badhiya! Aap bahut consistent hain! "
        elif habit_pct >= 50:
            review += "Theek hai! Aur mehnat karo agle hafte! "
        else:
            review += "Thoda aur focus karo apni habits pe! "

    review += "Agle hafte aur accha karo Krishna!"
    return review