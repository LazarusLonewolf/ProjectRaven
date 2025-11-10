# test_soft_runtime_monitor.py

import sys
import os

opt_path = os.path.join(os.path.dirname(__file__))
if opt_path not in sys.path:
    sys.path.append(opt_path)

import soft_runtime_monitor

def test_runtime_awareness():
    print("[TEST] Starting runtime awareness test...")

    status = soft_runtime_monitor.runtime_status()

    print(f"[TEST] Context: {status['context']}")
    print(f"[TEST] Start Time: {status['started_at']}")
    print(f"[TEST] Uptime (readable): {status['uptime']}")
    print(f"[TEST] Uptime (seconds): {status['uptime_seconds']}")
    print(f"[TEST] Status: {status['status']}")

if __name__ == "__main__":
    test_runtime_awareness()