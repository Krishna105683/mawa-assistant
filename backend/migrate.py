import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'nova.db')

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Add user_id to all tables
tables = ['habits', 'daily_routine', 'tasks', 'reminders']
for table in tables:
    try:
        cur.execute(f'ALTER TABLE {table} ADD COLUMN user_id INTEGER DEFAULT 0')
        print(f'Added user_id to {table}')
    except Exception as e:
        print(f'{table}: {e}')

conn.commit()
conn.close()
print('Migration done!')