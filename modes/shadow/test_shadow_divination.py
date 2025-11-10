# test_shadow_divination.py – CLI test for Shadow Mode with divination inputs

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from shadow_mode import ShadowMode

class MockUser:
    def __init__(self):
        self.profile = {"name": "Casey"}
    def get(self, key, default=None):
        return self.profile.get(key, default)

class MockMemory:
    pass

def run_test():
    print("=== Shadow Mode Divination Test ===")
    sm = ShadowMode(MockUser(), MockMemory())

    print("\n>>> Activating Shadow Mode...")
    print(sm.activate())

    inputs = [
        "Can you do a tarot reading for me?",
        "What does my numerology say for 1981-06-20?",
        "I need a natural remedy for anxiety."
    ]

    for text in inputs:
        print(f"\n>>> Input: {text}")
        response = sm.process_input(text)
        print(response)

if __name__ == "__main__":
    run_test()
