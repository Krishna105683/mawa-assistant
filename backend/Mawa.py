import os
import re
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from intents import detect_intent
from database import init_db, add_task, get_tasks, complete_task, delete_task, get_reminders
from weather_news import get_weather, get_news
from reminder import set_reminder, start_reminder_thread
from routine import init_routine_db, get_morning_briefing, add_habit, get_today_habits, complete_habit, get_habit_streak, add_routine_activity, get_daily_routine, get_weekly_review
from voice import speak, listen, detect_language

load_dotenv()
init_db()
init_routine_db()
start_reminder_thread(speak)

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
    time_pattern = r'(at|by|baje)\s+(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)'
    match = re.search(time_pattern, message, re.IGNORECASE)
    if match:
        return match.group(2).strip()
    period_pattern = r'in\s+(\d+\s+(?:hour|hours|day|days|week|weeks|minute|minutes|ghante|din|hafte))'
    match = re.search(period_pattern, message, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_task(message):
    task = message.lower()
    for word in ["add task", "new task", "todo", "to do", "to-do", "add",
                 "create task", "task add karo", "task add kar", "yaad dilao"]:
        task = task.replace(word, "").strip()
    task = re.sub(r'(at|by|baje)\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?', '', task, flags=re.IGNORECASE)
    task = re.sub(r'in\s+\d+\s+(?:hour|hours|day|days|week|weeks|ghante|din|hafte)', '', task, flags=re.IGNORECASE)
    return task.strip()

def chat(user_message, language="english"):
    if language == "hindi":
        lang_instruction = "IMPORTANT: Respond in Hindi/Hinglish ONLY."
    else:
        lang_instruction = "IMPORTANT: Respond in English ONLY. Do NOT use Hindi at all."

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

    mawa_reply = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": mawa_reply
    })

    return mawa_reply

def get_greeting():
    now = datetime.now()
    hour = now.hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def get_greeting_hindi():
    now = datetime.now()
    hour = now.hour
    if hour < 12:
        return "Suprabhat"
    elif hour < 17:
        return "Namaskar"
    else:
        return "Shubh Sandhya"

def handle_intent(intent, user_message, language="english"):
    now = datetime.now()
def handle_intent(intent, user_message, language="english"):
    now = datetime.now()

    if intent == "get_time":
        if language == "hindi":
            return f"Krishna, abhi {now.strftime('%I:%M %p')} baj rahe hain!"
        return f"The current time is {now.strftime('%I:%M %p')} Krishna!"

    elif intent == "get_date":
        if language == "hindi":
            return f"Krishna, aaj {now.strftime('%A, %d %B %Y')} hai!"
        return f"Today is {now.strftime('%A, %B %d, %Y')} Krishna!"

    elif intent == "add_task":
        task = extract_task(user_message)
        due_time = extract_time(user_message)
        if task:
            add_task(task, due_time)
            if language == "hindi":
                if due_time:
                    return f"Krishna, '{task}' {due_time} ke liye add ho gaya!"
                return f"Krishna, '{task}' aapki task list mein add ho gaya!"
            else:
                if due_time:
                    return f"Got it Krishna! I saved '{task}' due at {due_time}!"
                return f"Got it Krishna! '{task}' added to your task list!"
        else:
            if language == "hindi":
                return "Krishna, kaunsa task add karna hai?"
            return "What task would you like me to add Krishna?"

    elif intent == "show_tasks":
        tasks = get_tasks()
        if tasks:
            if language == "hindi":
                task_list = ""
                for t in tasks:
                    time_info = f" - {t[2]} baje" if t[2] else ""
                    task_list += f" Task {t[0]}: {t[1]}{time_info}."
                return f"Krishna, aapke {len(tasks)} pending tasks hain.{task_list}"
            else:
                task_list = ""
                for t in tasks:
                    time_info = f" at {t[2]}" if t[2] else ""
                    task_list += f" Task {t[0]}: {t[1]}{time_info}."
                return f"You have {len(tasks)} pending tasks Krishna.{task_list}"
        else:
            if language == "hindi":
                return "Krishna, abhi koi pending task nahi hai!"
            return "You have no pending tasks Krishna!"

    elif intent == "complete_task":
        numbers = re.findall(r'\d+', user_message)
        if numbers:
            task_id = int(numbers[0])
            complete_task(task_id)
            if language == "hindi":
                return f"Shabash Krishna! Task {task_id} complete ho gaya!"
            return f"Great job Krishna! Task {task_id} marked as done!"
        else:
            if language == "hindi":
                return "Krishna, kaunsa task number complete karna hai?"
            return "Please say the task number you want to complete Krishna!"

    elif intent == "get_weather":
        return get_weather()

    elif intent == "get_news":
        return get_news()
    elif intent == "set_reminder":
        import re
        message_lower = user_message.lower()
        
        for word in ["remind me to", "remind me", "reminder", "set reminder",
                     "yaad dila", "yaad dilao", "alert me to", "alert me"]:
            message_lower = message_lower.replace(word, "").strip()
        
        time_str = None
        title = message_lower

        time_match = re.search(
            r'(at\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?|in\s+\d+\s+[a-zA-Z]+|after\s+\d+\s+[a-zA-Z]+)',
            message_lower, re.IGNORECASE
        )

        # Fix common typos
        if time_match:
            time_str_raw = time_match.group(0)
            time_str_raw = time_str_raw.replace("after", "in")
            time_str_raw = time_str_raw.replace("mintues", "minutes")
            time_str_raw = time_str_raw.replace("mintue", "minutes")
            time_str_raw = time_str_raw.replace("minuts", "minutes")
            time_str_raw = time_str_raw.replace("mtues", "minutes")
            time_str = time_str_raw.replace("at", "").replace("in", "").strip()
            title = message_lower.replace(time_match.group(0), "").strip()
        else:
            time_str = None
            title = message_lower
        
    

        if time_match:
            time_str = time_match.group(0).replace("at", "").replace("in", "").strip()
            title = message_lower.replace(time_match.group(0), "").strip()

        if title and time_str:
            remind_at = set_reminder(title, time_str)
            if remind_at:
                if language == "hindi":
                    return f"Krishna, '{title}' ke liye {remind_at} ko reminder set ho gaya!"
                return f"Got it Krishna! I will remind you to '{title}' at {remind_at}!"
            else:
                if language == "hindi":
                    return "Krishna, reminder ka time samajh nahi aaya!"
                return "Sorry Krishna, I couldn't understand the time. Please try again!"
        else:
            if language == "hindi":
                return "Krishna, kya yaad dilana hai aur kab?"
            return "Krishna, what should I remind you about and when?"
    elif intent == "set_reminder":
        import re
        message_lower = user_message.lower()

        time_match = re.search(
            r'(at\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?|(?:in|after)\s+\d+\s+\w+)',
            message_lower, re.IGNORECASE
        )

        if time_match:
            raw_time = time_match.group(0)

            fixed_time = raw_time
            fixed_time = fixed_time.replace("after", "in")
            fixed_time = fixed_time.replace("mintues", "minutes")
            fixed_time = fixed_time.replace("mintue", "minutes")
            fixed_time = fixed_time.replace("minuts", "minutes")
            fixed_time = fixed_time.replace("mtues", "minutes")
            fixed_time = fixed_time.replace("mutes", "minutes")
            fixed_time = fixed_time.replace("minte", "minutes")
            fixed_time = fixed_time.replace("houres", "hours")
            fixed_time = fixed_time.replace("horus", "hours")

            time_str = fixed_time.replace("at", "").replace("in", "").strip()

            title = message_lower
            for word in ["remind me to", "remind me", "set reminder",
                        "reminder", "alert me to", "alert me",
                        "yaad dila", "yaad dilao"]:
                title = title.replace(word, "").strip()

            title = title.replace(raw_time, "").strip()
            title = title.strip(".,! ")

            if title and time_str:
                remind_at = set_reminder(title, time_str)
                if remind_at:
                    if language == "hindi":
                        return f"Krishna, '{title}' ke liye {remind_at} ko reminder set ho gaya!"
                    return f"Got it Krishna! I will remind you to '{title}' at {remind_at}!"
                else:
                    if language == "hindi":
                        return "Krishna, reminder ka time samajh nahi aaya!"
                    return "Sorry Krishna, I couldn't understand the time. Please try again!"
            else:
                if language == "hindi":
                    return "Krishna, kya yaad dilana hai aur kab?"
                return "Krishna, what should I remind you about and when?"
        else:
            if language == "hindi":
                return "Krishna, reminder ka time batao! Jaise: '5 minutes mein' ya 'at 8 PM'"
            return "Krishna, please tell me when! Example: 'in 5 minutes' or 'at 8 PM'"

    elif intent == "show_reminders":
        from database import get_reminders
        reminders = get_reminders()
        if reminders:
            if language == "hindi":
                reminder_list = ""
                for r in reminders:
                    reminder_list += f" {r[0]}. {r[1]} - {r[2]}."
                return f"Krishna, aapke {len(reminders)} reminders hain:{reminder_list}"
            else:
                reminder_list = ""
                for r in reminders:
                    reminder_list += f" {r[0]}. {r[1]} at {r[2]}."
                return f"You have {len(reminders)} reminders Krishna:{reminder_list}"
        else:
            if language == "hindi":
                return "Krishna, abhi koi reminder nahi hai!"
            return "You have no reminders set Krishna!"
        
    elif intent == "greeting":
        if language == "hindi":
            greet = get_greeting_hindi()
            return f"{greet} Krishna! Main Mawa hoon, aapki personal assistant. Aaj main aapki kya madad kar sakti hoon?"
        else:
            greet = get_greeting()
            return f"{greet} Krishna! I am Mawa, your personal assistant. How can I help you today?"
    elif intent == "add_habit":
        habit = user_message.lower()
        for word in ["add habit", "new habit", "track habit",
                     "habit add", "habit banana"]:
            habit = habit.replace(word, "").strip()
        if habit:
            add_habit(habit)
            if language == "hindi":
                return f"Krishna, '{habit}' habit track karna shuru ho gaya!"
            return f"Got it Krishna! I will track '{habit}' as your daily habit!"
        else:
            if language == "hindi":
                return "Krishna, kaunsi habit track karni hai?"
            return "What habit would you like to track Krishna?"

    elif intent == "show_habits":
        habits = get_today_habits()
        if habits:
            if language == "hindi":
                habit_list = ""
                for h in habits:
                    status = "✅" if h[2] == 1 else "⬜"
                    streak = get_habit_streak(h[1])
                    habit_list += f" {h[0]}. {status} {h[1]} (streak: {streak} days)."
                return f"Krishna, aaj ki habits:{habit_list}"
            else:
                habit_list = ""
                for h in habits:
                    status = "✅" if h[2] == 1 else "⬜"
                    streak = get_habit_streak(h[1])
                    habit_list += f" {h[0]}. {status} {h[1]} (streak: {streak} days)."
                return f"Here are today's habits Krishna:{habit_list}"
        else:
            if language == "hindi":
                return "Krishna, abhi koi habit track nahi ho rahi! 'Add habit' bol ke add karo!"
            return "No habits tracked yet Krishna! Say 'add habit' to start tracking!"

    elif intent == "add_routine":
        import re
        message_lower = user_message.lower()
        for word in ["add routine", "set routine", "daily routine",
                     "routine add", "routine set"]:
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
        return "Please tell me the activity and time Krishna! Example: 'add routine exercise at 6:00 AM'"

    elif intent == "show_routine":
        routine = get_daily_routine()
        if routine:
            if language == "hindi":
                routine_list = ""
                for r in routine:
                    routine_list += f" {r[0]}. {r[1]} - {r[2]}."
                return f"Krishna, aapka daily routine:{routine_list}"
            else:
                routine_list = ""
                for r in routine:
                    routine_list += f" {r[0]}. {r[1]} - {r[2]}."
                return f"Here is your daily routine Krishna:{routine_list}"
        else:
            if language == "hindi":
                return "Krishna, abhi koi routine set nahi hai! 'Add routine' bol ke add karo!"
            return "No routine set yet Krishna! Say 'add routine' to set one!"

    elif intent == "weekly_review":
        return get_weekly_review()

    elif intent == "morning_briefing":
        from database import get_reminders as fetch_reminders
        return get_morning_briefing(get_weather, get_tasks, fetch_reminders)
    
    elif intent == "goodbye":
        if language == "hindi":
            return "Alvida Krishna! Apna khayal rakhna!"
        return "Goodbye Krishna! Have a wonderful day!"

    else:
        return chat(user_message, language)

# Morning briefing
now = datetime.now()
hour = now.hour
weather = get_weather()
weather_short = weather.split('\n')[1] if '\n' in weather else weather
tasks = get_tasks()
task_count = len(tasks)

if hour < 12:
    briefing = f"Suprabhat Krishna! Main Mawa hoon. Aaj {now.strftime('%A, %d %B')} hai. {weather_short}. "
    briefing += f"Aapke {task_count} pending tasks hain." if task_count > 0 else "Koi pending task nahi hai."
elif hour < 17:
    briefing = f"Namaskar Krishna! {weather_short}. Kya kaam hai?"
else:
    briefing = f"Shubh Sandhya Krishna! {weather_short}. "
    briefing += f"Aapke {task_count} pending tasks hain abhi bhi." if task_count > 0 else "Koi pending task nahi."

print("=" * 50)
print("   MAWA - Aapki Personal Voice Assistant")
print("=" * 50)
print("Hindi ya English - dono mein baat karo!")
print("Press Ctrl+C to stop\n")

speak(briefing)

while True:
    try:
        mode = input("\nPress ENTER to speak or type your message: ")

        if mode.strip() == "":
            user_input, language = listen()
            if user_input is None:
                continue
        else:
            user_input = mode.strip()
            language = detect_language(user_input)

        if not user_input:
            continue

        intent = detect_intent(user_input)
        response = handle_intent(intent, user_input, language)
        speak(response)

        if intent == "goodbye":
            break

    except KeyboardInterrupt:
        speak("Alvida Krishna! Apna khayal rakhna!")
        break