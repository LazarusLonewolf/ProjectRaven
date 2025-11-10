# test_growth_monitor.py

import sys
sys.path.append("/app")

from analysis.growth_monitor import (
    load_growth_log, update_growth,
    analyze_progress, suggest_upgrades
)

def run_test():
    sample_detection = {
        "build routine": True,
        "reduce stress": False,
        "improve sleep": True,
        "increase creativity": False,
        "practice mindfulness": True,
        "reconnect with others": False,
        "maintain focus": True,
        "track emotional state": False
    }

    print("[TEST] Updating growth log with sample goal detection...")
    update_growth(sample_detection)

    print("[TEST] Reloading and analyzing progress...")
    growth_log = load_growth_log()
    progress = analyze_progress(growth_log)

    print("\n[RESULT] Goal Progress Overview:")
    for goal, summary in progress.items():
        print(f" - {goal}: {summary}")

    print("\n[RESULT] Upgrade Suggestions:")
    upgrades = suggest_upgrades(growth_log)
    for suggestion in upgrades:
        print(f" - {suggestion}")

if __name__ == "__main__":
    run_test()

