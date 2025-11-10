import sys, os

# Add path to `/app/` so memory, utilities, and modes are visible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utilities.raven_baseline_debugger import raven_debug_wrap
from comfort_mode import ComfortMode
from memory import emotional_tagging

# Mock analyzer
def mock_emotional_tagging(user_input):
    user_input = user_input.lower()
    if "ashamed" in user_input or "embarrassed" in user_input:
        return "shame"
    if "overwhelmed" in user_input:
        return "overwhelm"
    if "silent" in user_input or "numb" in user_input:
        return "silence"
    if "disconnected" in user_input or "avoiding" in user_input:
        return "withdrawal"
    if "panic" in user_input or "grief" in user_input:
        return "distress"
    return "neutral"

# Override analyzer
emotional_tagging.analyze = mock_emotional_tagging

class MockUser:
    name = "Casey"

class MockMemory:
    pass

@raven_debug_wrap(tag="COMFORT_MODE_TEST_BLOCK")
def run_test():
    cm = ComfortMode(MockUser(), MockMemory())

    print("=== Activate Mode ===")
    print(cm.activate())

    test_inputs = [
        "I’m just checking in.",                      # neutral
        "I feel really ashamed of how I handled it.", # shame
        "Everything is overwhelming right now.",      # overwhelm
        "I’ve just been silent. Can’t say anything.", # silence
        "I’m avoiding everyone lately.",              # withdrawal
        "I’m having a full panic moment here."        # distress
    ]

    for text in test_inputs:
        print(f"\n>>> Input: {text}")
        print(cm.process_input(text))

run_test()
