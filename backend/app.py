from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from auth import init_users_db, register_user, login_user, complete_setup
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
from groq import Groq
from database import init_db, add_task, get_tasks, complete_task, delete_task, get_reminders, add_reminder
from routine import init_routine_db, get_morning_briefing, add_habit, get_today_habits, complete_habit, get_habit_streak, add_routine_activity, get_daily_routine, get_weekly_review
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
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "mawa-secret-key-2024")
jwt = JWTManager(app)

init_db()
init_routine_db()
init_users_db()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are Mawa, Always address the user by their name from the conversation context.
Location: Hyderabad, India

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
    
    elif intent == "play_spotify":
        music_query = user_message.lower()
        for word in ["play on spotify", "spotify play", "spotify mein bajao",
                     "open spotify", "spotify pe bajao", "on spotify", "spotify", "play"]:
            music_query = music_query.replace(word, "").strip()
        if music_query:
            spotify_url = f"https://open.spotify.com/search/{music_query.replace(' ', '%20')}"
            if language == "hindi":
                return f"Krishna, '{music_query}' Spotify pe search kar raha hoon! Link: {spotify_url}"
            return f"Searching '{music_query}' on Spotify Krishna! Link: {spotify_url}"
        else:
            spotify_url = "https://open.spotify.com"
            if language == "hindi":
                return f"Krishna, Spotify khol raha hoon! Link: {spotify_url}"
            return f"Opening Spotify for you Krishna! Link: {spotify_url}"

    elif intent == "play_jiosaavn":
        music_query = user_message.lower()
        for word in ["play on jiosaavn", "jiosaavn play", "jiosaavn pe bajao",
                     "saavn pe bajao", "open jiosaavn", "jiosaavn"]:
            music_query = music_query.replace(word, "").strip()
        if music_query:
            url = f"https://www.jiosaavn.com/search/{music_query.replace(' ', '%20')}"
            if language == "hindi":
                return f"Krishna, '{music_query}' JioSaavn pe search kar raha hoon! Link: {url}"
            return f"Searching '{music_query}' on JioSaavn Krishna! Link: {url}"
        else:
            return f"Opening JioSaavn for you Krishna! Link: https://www.jiosaavn.com"

    elif intent == "play_gaana":
        music_query = user_message.lower()
        for word in ["play on gaana", "gaana play", "gaana pe bajao",
                     "open gaana", "gaana.com"]:
            music_query = music_query.replace(word, "").strip()
        if music_query:
            url = f"https://gaana.com/search/track/{music_query.replace(' ', '%20')}"
            if language == "hindi":
                return f"Krishna, '{music_query}' Gaana pe search kar raha hoon! Link: {url}"
            return f"Searching '{music_query}' on Gaana Krishna! Link: {url}"
        else:
            return f"Opening Gaana for you Krishna! Link: https://gaana.com"

    elif intent == "play_music":
        music_query = user_message.lower()
        for word in ["play music", "play song", "play songs", "play",
                     "gaana bajao", "music bajao", "song bajao",
                     "gaana chalaao", "music play"]:
            music_query = music_query.replace(word, "").strip()
        
        if music_query:
            from music import search_jiosaavn
            songs = search_jiosaavn(music_query)
            if songs:
                return {"type": "music", "data": songs, "query": music_query}
            else:
                youtube_url = f"https://www.youtube.com/results?search_query={music_query.replace(' ', '+')}"
                if language == "hindi":
                    return f"Krishna, JioSaavn pe nahi mila! YouTube try karo: {youtube_url}"
                return f"Couldn't find on JioSaavn! Try YouTube Krishna: {youtube_url}"
        else:
            if language == "hindi":
                return "Krishna, kaunsa gaana bajana hai? Batao!"
            return "What song would you like to play Krishna?"
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
    user_id = request.args.get('user_id', 0)
    tasks = get_tasks(user_id)
    return jsonify([{"id": t[0], "task": t[1], "time": t[2]} for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    user_id = data.get('user_id', 0)
    add_task(data['task'], data.get('time'), user_id)
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
    user_id = request.args.get('user_id', 0)
    reminders = get_reminders(user_id)
    return jsonify([{"id": r[0], "title": r[1], "time": r[2]} for r in reminders])

@app.route('/api/habits', methods=['GET'])
def get_all_habits():
    user_id = request.args.get('user_id', 0)
    habits = get_today_habits(user_id)
    return jsonify([{"id": h[0], "name": h[1], "done": h[2]} for h in habits])

@app.route('/api/habits/<int:habit_id>/complete', methods=['POST'])
def mark_habit_done(habit_id):
    complete_habit(habit_id)
    return jsonify({"success": True})

@app.route('/api/routine', methods=['GET'])
def get_routine():
    user_id = request.args.get('user_id', 0)
    routine = get_daily_routine(user_id)
    return jsonify([{"id": r[0], "activity": r[1], "time": r[2]} for r in routine])

@app.route('/api/weather', methods=['GET'])
def weather():
    lat = request.args.get('lat', None)
    lon = request.args.get('lon', None)
    return jsonify({"weather": get_weather(lat, lon)})

@app.route('/api/news', methods=['GET', 'OPTIONS'])
@cross_origin()
def news():
    return jsonify({"news": get_news()})

@app.route('/api/briefing', methods=['GET'])
def briefing():
    try:
        import pytz
        from datetime import datetime
        from database import get_reminders as fetch_reminders
        IST = pytz.timezone('Asia/Kolkata')
        now = datetime.now(IST)
        tasks = get_tasks()
        reminders = fetch_reminders()
        lat = request.args.get('lat', None)
        lon = request.args.get('lon', None)
        city = request.args.get('city', 'Hyderabad')
        hour = now.hour
        if hour < 12:
            greeting = "Suprabhat"
        elif hour < 17:
            greeting = "Namaskar"
        else:
            greeting = "Shubh Sandhya"
        briefing_text = f"{greeting}! Aaj {now.strftime('%A, %d %B %Y')} hai. "
        if tasks:
            briefing_text += f"Aapke {len(tasks)} pending tasks hain. "
        else:
            briefing_text += "Koi pending task nahi hai. "
        if reminders:
            briefing_text += f"Aapke {len(reminders)} reminders set hain. "
        briefing_text += "Batao kya madad chahiye?"
        return jsonify({"briefing": briefing_text})
    except Exception as e:
        return jsonify({"briefing": f"Good day! Mawa is here to help! Error: {str(e)}"})
    
@app.route('/api/music/search', methods=['GET'])
def music_search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"songs": []})
    from music import search_jiosaavn
    songs = search_jiosaavn(query)
    return jsonify({"songs": songs})

@app.route('/api/music/song/<song_id>', methods=['GET'])
def get_song(song_id):
    from music import get_song_url
    url = get_song_url(song_id)
    return jsonify({"url": url})    
# Keep alive ping
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "alive", "message": "Mawa is awake!"})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name', '')
    email = data.get('email', '')
    password = data.get('password', '')
    if not name or not email or not password:
        return jsonify({"success": False, "error": "All fields required!"})
    result = register_user(name, email, password)
    if result["success"]:
        token = create_access_token(identity=str(result["user_id"]))
        return jsonify({"success": True, "token": token, "name": name, "setup_done": 0})
    return jsonify(result)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required!"})
    result = login_user(email, password)
    if result["success"]:
        token = create_access_token(identity=str(result["user_id"]))
        return jsonify({"success": True, "token": token, "name": result["name"], "language": result["language"], "setup_done": result["setup_done"]})
    return jsonify(result)

@app.route('/api/setup', methods=['POST'])
def setup():
    data = request.json
    user_id = data.get('user_id')
    language = data.get('language', 'english')
    complete_setup(user_id, language)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
if __name__ == '__main__':
    app.run(debug=True, port=5000)