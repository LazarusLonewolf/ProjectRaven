# soft_runtime_monitor.py

import time
from datetime import datetime, timedelta

START_TIME = time.time()
CONTEXT_TAG = "runtime"

def get_uptime_seconds():
    return time.time() - START_TIME

def get_uptime_readable():
    delta = timedelta(seconds=int(get_uptime_seconds()))
    return str(delta)

def get_start_time_iso():
    return datetime.fromtimestamp(START_TIME).isoformat()

def runtime_status():
    return {
        "context": CONTEXT_TAG,
        "started_at": get_start_time_iso(),
        "uptime": get_uptime_readable(),
        "uptime_seconds": int(get_uptime_seconds()),
        "status": "active"
    }

if __name__ == "__main__":
    status = runtime_status()
    print("Raven Runtime Monitor:")
    for k, v in status.items():
        print(f"{k}: {v}")