
# growth_tracker.py – Tracks changes in seed structure for Raven's memory

import os
import json
from datetime import datetime
from raven_path_initializer import get_full_path

SEED_DIR = get_full_path("self_growth/memory/garden/seeds")
LOG_FILE = get_full_path("self_growth/memory/garden/seed_scan_log.json")

def log_growth_snapshot():
    structure = {}
    for root, _, files in os.walk(SEED_DIR):
        relative_path = os.path.relpath(root, SEED_DIR)
        structure[relative_path] = [f for f in files if f.endswith(".md")]

    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "structure": structure
    }

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([snapshot], f, indent=2)
    else:
        with open(LOG_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(snapshot)
            f.seek(0)
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    log_growth_snapshot()
