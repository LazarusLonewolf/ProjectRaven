import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utilities.raven_baseline_debugger import raven_debug_wrap
from childsafe_mode import ChildSafeMode
from memory import emotional_tagging

# Kid-safe emotional parsing
def mock_emotional_tagging(user_input):
    user_input = user_input.lower()
    if "scared" in user_input or "nervous" in user_input:
        return "fear"
    if "don't get it" in user_input or "i'm confused" in user_input:
        return "confusion"
    if "no one's around" in user_input or "feel alone" in user_input:
        return "lonely"
    return "neutral"

emotional_tagging.analyze = mock_emotional_tagging

class MockUser:
    name = "Connor"

class MockMemory:
    pass

@raven_debug_wrap(tag="CHILDSAFE_MODE_TEST")
def run_test():
    cm = ChildSafeMode(MockUser(), MockMemory())

    print("=== Activate Mode ===")
    print(cm.activate())

    test_inputs = [
        "Hi there.",                               # neutral
        "I don’t get it...",                       # confusion
        "I’m really nervous about tomorrow.",      # fear
        "No one’s around me right now."            # lonely
    ]

    for text in test_inputs:
        print(f"\n>>> Input: {text}")
        print(cm.process_input(text))

run_test()
