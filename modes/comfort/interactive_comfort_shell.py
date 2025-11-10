# interactive_comfort_shell.py
# CLI interface to Comfort Mode for manual input testing

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from comfort_mode import ComfortMode

class MockUser:
    def get(self, key, default=None):
        return "Casey"

class MockMemory:
    pass

if __name__ == "__main__":
    cm = ComfortMode(MockUser(), MockMemory())
    print(cm.activate())
    
    try:
        while True:
            user_input = input("\n>>> You: ")
            if user_input.lower() in ["exit", "quit"]:
                print(cm.deactivate())
                break
            response = cm.process_input(user_input)
            print(response)
    except KeyboardInterrupt:
        print("\n[Session ended]")
