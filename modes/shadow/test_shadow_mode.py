import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utilities.raven_baseline_debugger import raven_debug_wrap
from shadow_mode import ShadowMode
from memory import emotional_tagging

# Simulated tone for shadow-level inputs
def mock_emotional_tagging(user_input):
    user_input = user_input.lower()
    if "shame" in user_input:
        return "shame"
    if "angry" in user_input or "furious" in user_input:
        return "anger"
    if "resent" in user_input:
        return "resentment"
    if "not true" in user_input or "that’s not me" in user_input:
        return "denial"
    return "neutral"

emotional_tagging.analyze = mock_emotional_tagging

MockUser = {"name": "Casey"}

class MockMemory:
    pass

@raven_debug_wrap(tag="SHADOW_MODE_TEST")
def run_test():
    sm = ShadowMode(MockUser, MockMemory())

    print("=== Activate Mode ===")
    print(sm.activate())

    test_inputs = [
        "I’m just checking in again.",                   # neutral
        "I’m ashamed of how I acted.",                   # shame
        "I’m so angry at everything right now.",         # anger
        "I resent how much I’ve had to carry.",          # resentment
        "That’s not even true. That’s not who I am."     # denial
    ]

    for text in test_inputs:
        print(f"\n>>> Input: {text}")
        print(sm.process_input(text))

run_test()
