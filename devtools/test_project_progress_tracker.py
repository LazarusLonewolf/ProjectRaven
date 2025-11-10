# test_project_progress_tracker.py

import sys
import os

# Ensure the path to devtools is included
devtools_path = os.path.join(os.path.dirname(__file__))
if devtools_path not in sys.path:
    sys.path.append(devtools_path)

import project_progress_tracker as tracker

def run_progress_test():
    print("[TEST] Running Project Progress Tracker Test...")

    # Simulate logging a few project progress entries
    csv_path = tracker.log_project_progress("TestGameAlpha", "Pre-Production", "Initial structure planned.")
    tracker.log_project_progress("TestGameAlpha", "Prototype", "Core loop implemented.")
    tracker.log_project_progress("TestGameAlpha", "Testing", "Debug pass initiated.")

    # Retrieve and print the most recent entries
    entries = tracker.get_latest_entries()
    print("[TEST] Latest Project Log Entries:")
    for line in entries:
        print(line.strip())

    print(f"[TEST] Progress logged to: {csv_path}")

if __name__ == "__main__":
    run_progress_test()