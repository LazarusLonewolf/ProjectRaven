# test_session_state.py

import sys
import os
import time

# Ensure memory path is visible
sys.path.append("/app")

from memory.session_state import init_session_db, save_session_state, fetch_last_session

def run_test():
    print("[TEST] Initializing session DB...")
    init_session_db()

    test_mode = "comfort"
    test_emotions = ["curious", "hopeful"]

    print(f"[TEST] Saving session state: mode={test_mode}, emotions={test_emotions}")
    save_session_state(test_mode, test_emotions)

    time.sleep(1)  # Simulate brief interaction gap

    print("[TEST] Fetching last session...")
    session_data = fetch_last_session()

    print("[RESULT] Last session retrieved:")
    if session_data:
        print(f" - Timestamp: {session_data['timestamp']}")
        print(f" - Active Mode: {session_data['active_mode']}")
        print(f" - Emotion Tags: {session_data['emotion_tags']}")
    else:
        print(" - No session data found.")

if __name__ == "__main__":
    run_test()
