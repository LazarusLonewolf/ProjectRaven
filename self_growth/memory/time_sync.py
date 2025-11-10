# time_sync.py
# Reads system timezone info from config file

import os

CONFIG_PATH = "/app/config/timezone_info.txt"  # Adjust if the container mirrors this differently

def get_system_timezone():
    try:
        with open(CONFIG_PATH, "r") as file:
            timezone = file.read().strip()
            print(f"[TIME_SYNC] Detected system timezone: {timezone}")
            return timezone
    except FileNotFoundError:
        print("[TIME_SYNC] No timezone info found. Defaulting to 'UTC'")
        return "UTC"
