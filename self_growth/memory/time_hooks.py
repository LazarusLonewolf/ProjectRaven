# time_hooks.py

import os
import json
from datetime import datetime

CONFIG_PATH = "/app/config/system_time.json"

def get_current_time_segment():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = json.load(file)
            hour = config.get("hour", datetime.now().hour)
    except Exception:
        hour = datetime.now().hour

    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

def time_greeting():
    segment = get_current_time_segment()
    greetings = {
        "morning": "Good morning. Ready to start something meaningful?",
        "afternoon": "Good afternoon. Let’s keep moving forward.",
        "evening": "Good evening. How are you winding down today?",
        "night": "Late night, huh? Want to talk or just sit in silence?"
    }
    return greetings.get(segment, "Hello.")
