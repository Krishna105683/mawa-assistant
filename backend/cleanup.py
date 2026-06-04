import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'nova.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Delete duplicate task "to exercise"
cursor.execute("DELETE FROM tasks WHERE id = 5")
print("Deleted duplicate task: to exercise")

# Delete duplicate habit "to drink water"
cursor.execute("DELETE FROM habits WHERE id = 1")
print("Deleted duplicate habit: to drink water")

# Fix "to study books" to "study books"
cursor.execute("UPDATE habits SET name = 'study books' WHERE id = 6")
print("Fixed habit name: to study books → study books")

conn.commit()
conn.close()
print("\nDatabase cleaned successfully!")

# Verify
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n--- CLEAN TASKS ---")
cursor.execute("SELECT id, task, done FROM tasks")
for row in cursor.fetchall():
    status = "✅ done" if row[2] == 1 else "⬜ pending"
    print(f"  {row[0]}. {row[1]} — {status}")

print("\n--- CLEAN HABITS ---")
cursor.execute("SELECT id, name, completed FROM habits")
for row in cursor.fetchall():
    status = "✅ done" if row[2] == 1 else "⬜ pending"
    print(f"  {row[0]}. {row[1]} — {status}")

print("\n--- CLEAN REMINDERS ---")
cursor.execute("SELECT id, title, remind_at, done FROM reminders WHERE done = 0")
for row in cursor.fetchall():
    print(f"  {row[0]}. {row[1]} at {row[2]}")

conn.close()