import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from intents import detect_intent
from database import init_db, add_task, get_tasks, complete_task, delete_task
from weather_news import get_weather, get_news
from voice import speak, listen
import re

load_dotenv()

# Initialize database
init_db()

# Initialize Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are Mawa, a smart and friendly personal assistant for Krishna Kumar.
You help with:
- Daily reminders and schedules
- Tasks and to-do lists
- Daily routines and habits
- Weather and news updates
- General questions

Your personality:
- Friendly, helpful and professional
- Respond in short and clear sentences
- Always address the user as Krishna
- If you don't know something, say so honestly
- Keep responses under 3 sentences for voice

Current user: Krishna Kumar
Location: Hyderabad, India
"""

conversation_history = []

def extract_time(message):
    time_pattern = r'(at|by)\s+(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))'
    match = re.search(time_pattern, message, re.IGNORECASE)
    if match:
        return match.group(2).strip()
    period_pattern = r'in\s+(\d+\s+(?:hour|hours|day|days|week|weeks|minute|minutes))'
    match = re.search(period_pattern, message, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_task(message):
    task = message.lower()
    for word in ["add task", "new task", "todo", "to do", "to-do", "add", "create task"]:
        task = task.replace(word, "").strip()
    task = re.sub(r'(at|by)\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)', '', task, flags=re.IGNORECASE)
    task = re.sub(r'in\s+\d+\s+(?:hour|hours|day|days|week|weeks|minute|minutes)', '', task, flags=re.IGNORECASE)
    return task.strip()

def chat(user_message):
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + conversation_history
    )
    Mawa_reply = response.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": Mawa_reply
    })
    return Mawa_reply

def handle_intent(intent, user_message):
    now = datetime.now()

    if intent == "get_time":
        return f"The current time is {now.strftime('%I:%M %p')} Krishna!"

    elif intent == "get_date":
        return f"Today is {now.strftime('%A, %B %d, %Y')} Krishna!"

    elif intent == "add_task":
        task = extract_task(user_message)
        due_time = extract_time(user_message)
        if task:
            add_task(task, due_time)
            if due_time:
                return f"Got it Krishna! I saved {task} due at {due_time}!"
            else:
                return f"Got it Krishna! I saved {task} to your task list!"
        else:
            return "What task would you like me to add Krishna?"

    elif intent == "show_tasks":
        tasks = get_tasks()
        if tasks:
            task_list = ""
            for t in tasks:
                time_info = f" at {t[2]}" if t[2] else ""
                task_list += f" Task {t[0]}: {t[1]}{time_info}."
            return f"You have {len(tasks)} pending tasks Krishna.{task_list}"
        else:
            return "You have no pending tasks Krishna! Say add task to add one."

    elif intent == "complete_task":
        numbers = re.findall(r'\d+', user_message)
        if numbers:
            task_id = int(numbers[0])
            complete_task(task_id)
            return f"Great job Krishna! Task {task_id} marked as done!"
        else:
            return "Please say the task number you want to complete Krishna!"

    elif intent == "get_weather":
        return get_weather()

    elif intent == "get_news":
        return get_news()

    elif intent == "greeting":
        hour = now.hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        return f"{greeting} Krishna! How can I help you today?"

    elif intent == "goodbye":
        return "Goodbye Krishna! Have a wonderful day!"

    else:
        return chat(user_message)

# Main voice loop
print("=" * 50)
print("   Mawa - Your Personal Voice Assistant")
print("=" * 50)
print("Say 'bye' to exit")
print("Press Ctrl+C to stop at any time\n")

speak("Hello Krishna! I am Mawa, your personal voice assistant. How can I help you today?")

while True:
    try:
        # Choose input mode
        mode = input("\nPress ENTER to speak or type your message: ")
        
        if mode.strip() == "":
            # Voice mode
            user_input = listen()
            if user_input is None:
                continue
        else:
            # Text mode fallback
            user_input = mode.strip()

        if not user_input:
            continue

        intent = detect_intent(user_input)
        response = handle_intent(intent, user_input)
        speak(response)

        if intent == "goodbye":
            break

    except KeyboardInterrupt:
        speak("Goodbye Krishna!")
        break