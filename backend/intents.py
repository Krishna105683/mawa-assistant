import re

def detect_intent(message):
    message = message.lower().strip()
    
    # Show reminders - must be BEFORE set_reminder
    if any(word in message for word in ["show reminder", "show reminders",
                                         "my reminder", "my reminders",
                                         "list reminder", "reminder list",
                                         "reminders dikhao", "reminder dikhao"]):
        return "show_reminders"
    
    # Set reminder
    elif any(word in message for word in ["remind me", "remind", "reminder",
                                           "alert me", "alert", "notify",
                                           "yaad dila", "yaad dilao", "alarm"]):
        return "set_reminder"
    
    # Add task
    elif any(word in message for word in ["add task", "new task", "todo",
                                           "to do", "to-do", "create task",
                                           "add a task"]):
        return "add_task"
    
    # Show tasks - must be BEFORE add_task
    elif any(word in message for word in ["show task", "show tasks", "my task",
                                           "my tasks", "task list", "list task",
                                           "list tasks", "what are my task",
                                           "pending task", "view task",
                                           "see task", "mera task", "mere task",
                                           "task dikhao", "task batao",
                                           "task show", "apna task"]):
        return "show_tasks"
    
    # Complete task
    elif any(word in message for word in ["complete task", "done task",
                                           "finish task", "mark task"]):
        return "complete_task"
    
    # Schedule
    elif any(word in message for word in ["schedule", "calendar",
                                           "events", "appointments"]):
        return "show_schedule"
    
    # Weather
    elif any(word in message for word in ["weather", "temperature",
                                           "rain", "forecast", "mausam"]):
        return "get_weather"
    
    # News
    elif any(word in message for word in ["news", "headlines",
                                           "today's news", "latest news"]):
        return "get_news"
    
    # Greeting
    elif any(word in message for word in ["hello", "hi", "hey",
                                           "good morning", "good evening",
                                           "good afternoon", "namaste",
                                           "namaskar", "suprabhat"]):
        return "greeting"
    
    # Time
    elif any(word in message for word in ["what time", "current time",
                                           "time now", "time is it",
                                           "the time", "time please",
                                           "time kya", "kitne baje"]):
        return "get_time"
    
    # Date
    elif any(word in message for word in ["what date", "today's date",
                                           "what day", "current date",
                                           "date today", "day is it",
                                           "aaj kya", "aaj kon"]):
        return "get_date"
    # Habit intents
    elif any(word in message for word in ["add habit", "new habit", "track habit",
                                           "habit add", "habit banana"]):
        return "add_habit"

    elif any(word in message for word in ["show habit", "my habit", "habit list",
                                           "habits dikhao", "complete habit",
                                           "habit complete"]):
        return "show_habits"

    # Routine intents
    elif any(word in message for word in ["add routine", "set routine", "daily routine",
                                           "routine add", "routine set",
                                           "add to routine", "routine me add",
                                           "add meditation", "add wake", "add sleep",
                                           "add breakfast", "add exercise", "add study",
                                           "add lunch", "add dinner", "add workout"]):
        return "add_routine"

    elif any(word in message for word in ["show routine", "my routine", "routine dikhao",
                                           "aaj ka routine", "daily schedule"]):
        return "show_routine"

    # Weekly review
    elif any(word in message for word in ["weekly review", "week review", "this week",
                                           "hafte ka review", "week ka review"]):
        return "weekly_review"

    # Morning briefing
    elif any(word in message for word in ["morning briefing", "daily briefing",
                                           "aaj ka briefing", "briefing do"]):
        return "morning_briefing"
    # Goodbye
    elif any(word in message for word in ["bye", "goodbye", "see you",
                                           "exit", "quit", "alvida",
                                           "phir milenge"]):
        return "goodbye"
    
    # Default
    else:
        return "general"