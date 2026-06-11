from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
from groq import Groq
from database_pg import init_db, add_task, get_tasks, complete_task, delete_task, add_reminder, get_reminders, add_habit, get_today_habits, complete_habit, add_routine_activity, get_daily_routine
from routine import init_routine_db, get_morning_briefing, get_habit_streak, get_weekly_review
from weather_news import get_weather, get_news
from reminder import set_reminder, start_reminder_thread
from intents import detect_intent
import re

load_dotenv()

app = Flask(__name__)
CORS(app, 
     origins=["https://mawa-assistant.vercel.app", "http://localhost:3000", "*"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "DELETE", "OPTIONS"],
     supports_credentials=True)

init_db()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are Mawa, a personal assistant for Krishna Kumar in Hyderabad, India.

STRICT LANGUAGE RULE:
- When user speaks English respond in English ONLY
- When user speaks Hindi respond in Hindi ONLY
- NEVER mix languages unless user mixes them first

Keep responses short, friendly and under 3 sentences.
Always call the user Krishna.
"""

conversation_history = []

def extract_time(message):
    time_pattern = r'(at\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?|(?:in|after)\s+\d+\s+\w+)'
    match = re.search(time_pattern, message, re.IGNORECASE)
    if match:
        raw = match.group(0)
        raw = raw.replace("after", "in")
        return raw.replace("at", "").replace("in", "").strip(), match.group(0)
    return None, None

def extract_task(message, time_raw):
    task = message.lower()
    for word in ["add task", "new task", "todo", "to do", "to-do",
                 "add", "create task"]:
        task = task.replace(word, "").strip()
    if time_raw:
        task = task.replace(time_raw, "").strip()
    return task.strip()

def chat_with_mawa(user_message, language="english"):
    if language == "hindi":
        lang_instruction = "IMPORTANT: Respond in Hindi/Hinglish ONLY."
    else:
        lang_instruction = "IMPORTANT: Respond in English ONLY."

    conversation_history.append({
        "role": "user",
        "content": f"{lang_instruction}\nUser: {user_message}"
    })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + conversation_history
    )

    reply = response.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": reply
    })
    return reply

def handle_message(user_message, language="english"):
    intent = detect_intent(user_message)
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    if intent == "get_time":
        if language == "hindi":
            return f"Krishna, abhi {now.strftime('%I:%M %p')} baj rahe hain!"
        return f"The current time is {now.strftime('%I:%M %p')} Krishna!"

    elif intent == "get_date":
        if language == "hindi":
            return f"Krishna, aaj {now.strftime('%A, %d %B %Y')} hai!"
        return f"Today is {now.strftime('%A, %B %d, %Y')} Krishna!"

    elif intent == "add_task":
        time_str, time_raw = extract_time(user_message)
        task = extract_task(user_message, time_raw)
        if task:
            add_task(task, time_str)
            if language == "hindi":
                return f"Krishna, '{task}' task add ho gaya!"
            return f"Got it Krishna! '{task}' added to your task list!"
        return "What task would you like to add Krishna?"

    elif intent == "show_tasks":
        tasks = get_tasks()
        if tasks:
            task_list = [{"id": t[0], "task": t[1], "time": t[2]} for t in tasks]
            return {"type": "tasks", "data": task_list, "language": language}
        if language == "hindi":
            return "Krishna, abhi koi pending task nahi hai!"
        return "You have no pending tasks Krishna!"

    elif intent == "complete_task":
        numbers = re.findall(r'\d+', user_message)
        if numbers:
            complete_task(int(numbers[0]))
            return f"Task {numbers[0]} completed Krishna! ✅"
        return "Which task number Krishna?"

    elif intent == "set_reminder":
        time_match = re.search(
            r'(at\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?|(?:in|after)\s+\d+\s+\w+)',
            user_message.lower(), re.IGNORECASE
        )
        if time_match:
            raw_time = time_match.group(0)
            fixed_time = raw_time.replace("after", "in")
            for typo, fix in [("mintues","minutes"),("mintue","minutes"),
                               ("mutes","minutes"),("mtues","minutes")]:
                fixed_time = fixed_time.replace(typo, fix)
            time_str = fixed_time.replace("at","").replace("in","").strip()
            title = user_message.lower()
            for word in ["remind me to","remind me","reminder","set reminder"]:
                title = title.replace(word, "").strip()
            title = title.replace(raw_time, "").strip()
            remind_at = set_reminder(title, time_str)
            if remind_at:
                return f"Reminder set for '{title}' at {remind_at} Krishna!"
        return "Please tell me what and when to remind you Krishna!"

    elif intent == "show_reminders":
        reminders = get_reminders()
        if reminders:
            reminder_list = [{"id": r[0], "title": r[1], "time": r[2]} for r in reminders]
            return {"type": "reminders", "data": reminder_list}
        return "No reminders set Krishna!"

    elif intent == "get_weather":
        return get_weather()

    elif intent == "get_news":
        return get_news()

    elif intent == "add_habit":
        habit = user_message.lower()
        for word in ["add habit", "new habit", "track habit"]:
            habit = habit.replace(word, "").strip()
        if habit:
            add_habit(habit)
            return f"Habit '{habit}' added Krishna!"
        return "What habit would you like to track Krishna?"

    elif intent == "show_habits":
        habits = get_today_habits()
        if habits:
            habit_list = [{"id": h[0], "name": h[1], "done": h[2]} for h in habits]
            return {"type": "habits", "data": habit_list}
        return "No habits tracked yet Krishna!"
    elif intent == "add_routine":
        import re
        message_lower = user_message.lower()
        for word in ["add routine", "set routine", "daily routine",
                     "routine add", "routine set", "add to routine"]:
            message_lower = message_lower.replace(word, "").strip()

        time_match = re.search(
            r'(at\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)',
            message_lower, re.IGNORECASE
        )

        if time_match:
            time_str = time_match.group(0).replace("at", "").strip()
            activity = message_lower.replace(time_match.group(0), "").strip()
            if activity and time_str:
                add_routine_activity(activity, time_str)
                if language == "hindi":
                    return f"Krishna, '{activity}' {time_str} ko aapke daily routine mein add ho gaya!"
                return f"Got it Krishna! '{activity}' at {time_str} added to your daily routine!"

        if language == "hindi":
            return "Krishna, activity aur time batao! Jaise: 'add routine exercise at 6:00 AM'"
        return "Please tell me the activity and time! Example: 'add routine meditation at 7:00 AM'"
    elif intent == "show_routine":
        routine = get_daily_routine()
        if routine:
            routine_list = [{"id": r[0], "activity": r[1], "time": r[2]} for r in routine]
            return {"type": "routine", "data": routine_list}
        return "No routine set yet Krishna!"

    elif intent == "weekly_review":
        return get_weekly_review()

    elif intent == "morning_briefing":
        return get_morning_briefing(get_weather, get_tasks, get_reminders)

    elif intent == "greeting":
        hour = now.hour
        if language == "hindi":
            if hour < 12:
                return "Suprabhat Krishna! Main Mawa hoon, kya madad kar sakti hoon?"
            elif hour < 17:
                return "Namaskar Krishna! Kya kaam hai?"
            else:
                return "Shubh Sandhya Krishna! Kya madad chahiye?"
        else:
            if hour < 12:
                return "Good morning Krishna! How can I help you?"
            elif hour < 17:
                return "Good afternoon Krishna! What can I do for you?"
            else:
                return "Good evening Krishna! How can I help?"

    else:
        return chat_with_mawa(user_message, language)

# ─── API ROUTES ───────────────────────────────────────

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    language = data.get('language', 'english')
    response = handle_message(message, language)
    return jsonify({"response": response, "intent": detect_intent(message)})

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    tasks = get_tasks()
    return jsonify([{"id": t[0], "task": t[1], "time": t[2]} for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    add_task(data['task'], data.get('time'))
    return jsonify({"success": True})

@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def mark_task_done(task_id):
    complete_task(task_id)
    return jsonify({"success": True})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def remove_task(task_id):
    delete_task(task_id)
    return jsonify({"success": True})

@app.route('/api/reminders', methods=['GET'])
def get_all_reminders():
    reminders = get_reminders()
    return jsonify([{"id": r[0], "title": r[1], "time": r[2]} for r in reminders])

@app.route('/api/habits', methods=['GET'])
def get_all_habits():
    habits = get_today_habits()
    return jsonify([{"id": h[0], "name": h[1], "done": h[2]} for h in habits])

@app.route('/api/habits/<int:habit_id>/complete', methods=['POST'])
def mark_habit_done(habit_id):
    complete_habit(habit_id)
    return jsonify({"success": True})

@app.route('/api/routine', methods=['GET'])
def get_routine():
    routine = get_daily_routine()
    return jsonify([{"id": r[0], "activity": r[1], "time": r[2]} for r in routine])

@app.route('/api/weather', methods=['GET'])
def weather():
    return jsonify({"weather": get_weather()})

@app.route('/api/news', methods=['GET', 'OPTIONS'])
@cross_origin()
def news():
    return jsonify({"news": get_news()})

@app.route('/api/briefing', methods=['GET'])
def briefing():
    try:
        from database import get_reminders as fetch_reminders
        result = get_morning_briefing(get_weather, get_tasks, fetch_reminders)
        return jsonify({"briefing": result})
    except Exception as e:
        print(f"Briefing error: {str(e)}")
        from datetime import datetime
        import pytz
        IST = pytz.timezone('Asia/Kolkata')
        now = datetime.now(IST)
        return jsonify({"briefing": f"Good {'morning' if now.hour < 12 else 'afternoon' if now.hour < 17 else 'evening'} Krishna! Mawa is ready to help you today!"})
# Keep alive ping
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "alive", "message": "Mawa is awake!"})
if __name__ == '__main__':
    app.run(debug=True, port=5000)