import time
import threading
import re
from datetime import datetime, timedelta
from database import add_reminder, get_reminders
import sqlite3
import os

if os.environ.get('RENDER'):
    DB_PATH = '/tmp/nova.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'nova.db')
def parse_reminder_time(time_str):
    """Convert time string to datetime object"""
    now = datetime.now()
    time_str = time_str.strip().lower()
    
    # Fix typos FIRST before anything else
    time_str = time_str.replace("after", "")
    time_str = time_str.replace("mintues", "minutes")
    time_str = time_str.replace("mintue", "minutes")
    time_str = time_str.replace("minuts", "minutes")
    time_str = time_str.replace("mtues", "minutes")
    time_str = time_str.replace("mutes", "minutes")
    time_str = time_str.replace("minte", "minutes")
    time_str = time_str.replace("mits", "minutes")
    time_str = time_str.replace("houres", "hours")
    time_str = time_str.replace("horus", "hours")
    time_str = time_str.strip()
    
    print(f"Parsed time string: {time_str}")
    
    # Check for minutes
    if any(word in time_str for word in ["minute", "minutes", "min", "mins"]):
        numbers = re.findall(r'\d+', time_str)
        if numbers:
            return now + timedelta(minutes=int(numbers[0]))

    # Check for hours
    elif any(word in time_str for word in ["hour", "hours", "hr", "hrs"]):
        numbers = re.findall(r'\d+', time_str)
        if numbers:
            return now + timedelta(hours=int(numbers[0]))

    # Check for days
    elif any(word in time_str for word in ["day", "days"]):
        numbers = re.findall(r'\d+', time_str)
        if numbers:
            return now + timedelta(days=int(numbers[0]))

    # Check for weeks
    elif any(word in time_str for word in ["week", "weeks"]):
        numbers = re.findall(r'\d+', time_str)
        if numbers:
            return now + timedelta(weeks=int(numbers[0]))

    # Handle "at HH:MM AM/PM"
    else:
        try:
            if "am" in time_str or "pm" in time_str:
                clean_time = time_str.replace("at", "").strip().upper()
                try:
                    t = datetime.strptime(clean_time, "%I:%M %p")
                except:
                    t = datetime.strptime(clean_time, "%I %p")
            else:
                clean_time = time_str.replace("at", "").strip()
                t = datetime.strptime(clean_time, "%H:%M")

            remind_at = now.replace(
                hour=t.hour,
                minute=t.minute,
                second=0,
                microsecond=0
            )

            if remind_at < now:
                remind_at += timedelta(days=1)

            return remind_at

        except Exception as e:
            print(f"Time parse error: {e}")
            return None

def set_reminder(title, time_str):
    """Add reminder to database"""
    remind_at = parse_reminder_time(time_str)
    if remind_at:
        add_reminder(title, remind_at.strftime("%Y-%m-%d %H:%M:%S"))
        return remind_at.strftime("%I:%M %p on %A")
    return None

def check_reminders(speak_func):
    """Background thread that checks reminders every 30 seconds"""
    while True:
        try:
            now = datetime.now()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Get all pending reminders
            cursor.execute("""
                SELECT id, title, remind_at 
                FROM reminders 
                WHERE done = 0
            """)
            reminders = cursor.fetchall()
            conn.close()

            for reminder in reminders:
                rid, title, remind_at_str = reminder
                remind_at = datetime.strptime(remind_at_str, "%Y-%m-%d %H:%M:%S")

                # Check if reminder time has come (within 30 second window)
                diff = (now - remind_at).total_seconds()
                if 0 <= diff <= 30:
                    # Fire the reminder!
                    print(f"\n🔔 REMINDER: {title}")
                    speak_func(f"Krishna! Reminder! {title}")

                    # Mark as done
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE reminders SET done = 1 WHERE id = ?", (rid,))
                    conn.commit()
                    conn.close()

        except Exception as e:
            print(f"Reminder check error: {e}")

        # Check every 30 seconds
        time.sleep(30)

def start_reminder_thread(speak_func):
    """Start background reminder checker"""
    thread = threading.Thread(
        target=check_reminders,
        args=(speak_func,),
        daemon=True
    )
    thread.start()
    print("⏰ Reminder system started!")