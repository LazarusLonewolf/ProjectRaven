import sys
import os

# Force /app onto path so we can import memory.*
sys.path.append("/app")

import memory.time_hooks as time_hooks

def run_test():
    print("[TEST] Checking current time segment...")
    segment = time_hooks.get_current_time_segment()
    print(f"[RESULT] Current time segment: {segment}")

    print("[TEST] Retrieving context-aware greeting...")
    greeting = time_hooks.time_greeting()
    print(f"[RESULT] Greeting: {greeting}")

if __name__ == "__main__":
    run_test()