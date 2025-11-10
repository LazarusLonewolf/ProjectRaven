import sys
import os

sys.path.append("/app")

from memory.flags.flag_loader import get_flag

def run_test():
    print("[TEST] Retrieving sample flags...")
    for key in ["enable_journaling", "allow_voice_mode", "debug_mode", "auto_backup", "nonexistent_flag"]:
        value = get_flag(key)
        print(f" - {key}: {value}")

if __name__ == "__main__":
    run_test()
