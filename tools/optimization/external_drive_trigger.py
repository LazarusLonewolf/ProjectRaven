# external_drive_trigger.py

import json
from optimization import external_drive_monitor  # Corrected import

TRIGGER_FILE = "/app/optimization/external_drive_triggers.json"  # Absolute path

def load_triggers():
    try:
        with open(TRIGGER_FILE, 'r') as file:
            data = json.load(file)
            return data.get("external_drive_triggers", [])
    except Exception as e:
        print(f"Error loading triggers: {e}")
        return []

def normalize(text):
    return text.strip().lower()

def match_trigger(user_input):
    normalized_input = normalize(user_input)
    triggers = load_triggers()
    for phrase in triggers:
        if phrase in normalized_input:
            return True
    return False

def run_drive_scan_if_triggered(user_input):
    if match_trigger(user_input):
        print("Trigger matched. Running external drive scan...\n")
        drives = external_drive_monitor.list_external_drives()
        external_drive_monitor.notify_user(drives)
        return True
    else:
        print("No matching trigger found.")
        return False

if __name__ == "__main__":
    sample_input = input("Enter user command: ")
    run_drive_scan_if_triggered(sample_input)

