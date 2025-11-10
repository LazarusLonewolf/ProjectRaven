import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utilities.raven_baseline_debugger import raven_debug_wrap
from muse_mode import MuseMode
from memory import emotional_tagging

# Mock tone simulation for Muse Mode
def mock_emotional_tagging(user_input):
    user_input = user_input.lower()
    if "bored" in user_input:
        return "bored"
    if "inspired" in user_input:
        return "inspired"
    if "wonder" in user_input or "what if" in user_input:
        return "curious"
    return "neutral"

emotional_tagging.analyze = mock_emotional_tagging

class MockUser:
    name = "Casey"

class MockMemory:
    pass

@raven_debug_wrap(tag="MUSE_MODE_TEST")
def run_test():
    mm = MuseMode(MockUser(), MockMemory())

    print("=== Activate Mode ===")
    print(mm.activate())

    test_inputs = [
        "Just checking in again.",
        "I’m feeling kinda bored right now.",
        "I got this wild idea earlier...",
        "What if everything we see is only part true?"
    ]

    for text in test_inputs:
        print(f"\n>>> Input: {text}")
        print(mm.process_input(text))

run_test()


