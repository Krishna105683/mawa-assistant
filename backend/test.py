import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful personal assistant named Nova. You help with reminders, tasks, schedules and daily routines."
        },
        {
            "role": "user",
            "content": "Hello! Introduce yourself in 2 sentences."
        }
    ]
)

print(response.choices[0].message.content)