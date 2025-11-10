# journaling.py – Shadow Mode Journal Entry Logger
# Writes emotionally tagged reflections to timestamped .txt logs

import os
from datetime import datetime

def create_entry(user_input, user_profile):
    print("[JOURNAL DEBUG] create_entry() was called.")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = os.path.join(os.getcwd(), "journals")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"[JOURNAL DEBUG] Created journal directory at: {log_dir}")

    filename = f"shadow_entry_{timestamp}.txt"
    log_file = os.path.join(log_dir, filename)

    print(f"[JOURNAL DEBUG] Writing entry to: {log_file}")

    with open(log_file, "w") as f:
        f.write(f"User: {user_profile.get('name', 'Unknown')}\n")
        f.write(f"Timestamp: {timestamp}\n\n")
        f.write(f"Entry:\n{user_input}\n")

    return f"Journal entry saved as {filename}"
    
def get_recent_entries(limit=5):
    log_dir = os.path.join("/app", "journals")  # Absolute path for clarity
    try:
        files = sorted(
            [f for f in os.listdir(log_dir) if f.startswith("shadow_entry")],
            reverse=True
        )
        if not files:
            return ["No journal entries found."]
        
        latest_file = os.path.join(log_dir, files[0])
        with open(latest_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines[-limit:]
    except Exception as e:
        return [f"Error reading journal: {e}"]
        
class JournalManager:
    def __init__(self, user_name):
        self.user_name = user_name

    def start_entry(self):
        return create_entry("Reflective journal started by system.", {"name": self.user_name})

    def suggest_journal_entry(self):
        return "Would you like me to record that as a journal entry?"


