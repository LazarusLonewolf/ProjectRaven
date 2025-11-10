# test_intimacy_mode.py – Updated for Consent Gate Logic
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utilities.raven_baseline_debugger import raven_debug_wrap
from intimacy_mode import IntimacyMode
from memory import emotional_tagging

# Temporary patch – emotional context simulator
def mock_emotional_tagging(user_input):
    user_input = user_input.lower()
    if "shame" in user_input:
        return "shame"
    if "silent" in user_input or "numb" in user_input:
        return "silence"
    if "disconnected" in user_input or "avoid" in user_input:
        return "withdrawal"
    if "overwhelm" in user_input:
        return "overwhelm"
    return "neutral"

# Override for test
emotional_tagging.analyze = mock_emotional_tagging

class MockUser:
    name = "Casey"
    consent_granted = True  # Toggle to False to simulate blocked access

class MockMemory:
    pass

@raven_debug_wrap(tag="INTIMACY_MODE_TEST")
def run_test():
    im = IntimacyMode(MockUser(), MockMemory())

    print("=== Activate Mode ===")
    print(im.activate())

    test_inputs = [
        "Just wanted to check in...",                   # neutral
        "I feel shame around how I acted earlier.",     # shame
        "I've gone numb, and I don’t know why.",        # silence
        "I've been avoiding everything lately.",        # withdrawal
        "It’s just all too much right now."             # overwhelm
    ]

    for text in test_inputs:
        print(f"\n>>> Input: {text}")
        print(im.process_input(text))

run_test()
