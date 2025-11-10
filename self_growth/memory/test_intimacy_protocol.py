# test_intimacy_protocol.py

import sys
import os
sys.path.append("/app")

from memory.intimacy_protocol import IntimacyState

def run_test():
    print("[TEST] Initializing intimacy protocol...")
    state = IntimacyState()

    print(f"[CHECK] Initial level: {state.get_level()}")

    state.increase_intimacy(reason="consistent empathy detected")
    print(f"[CHECK] After increase: {state.get_level()} | Reason: {state.get_reason()}")

    state.increase_intimacy(amount=2, reason="shared memory recall")
    print(f"[CHECK] After further increase: {state.get_level()} | Reason: {state.get_reason()}")

    state.decrease_intimacy(reason="missed emotional cue")
    print(f"[CHECK] After decrease: {state.get_level()} | Reason: {state.get_reason()}")

    state.decrease_intimacy(amount=3, reason="context drop")
    print(f"[CHECK] After hard reset: {state.get_level()} | Reason: {state.get_reason()}")

if __name__ == "__main__":
    run_test()

