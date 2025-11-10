# childsafe_sandbox.py – Final Hybrid ChildSafe Sandbox
# Combines gentle emotional prompts, symbolic anchors, seed reflections, and sandbox lifecycle

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import random
from utilities.symbolics import childsafe_symbols
from modes.childsafe import childsafe_templates
from memory.session_emotion import emotion_tracker

class ChildSafeSandbox:
    def __init__(self, user_profile):
        self.user = user_profile
        self.active = False
        self.prompt_seed_bank = [
            "Can you tell me something kind someone said to you?",
            "What color makes you feel safe?",
            "What does your favorite cozy place look like?",
            "If you had a quiet bubble around you, what would it sound like?",
            "What makes you feel braver, even a little?",
            "Imagine you’re holding a soft glowing stone. What does it do?",
            "Who do you feel the safest with? Why?",
            "What’s something gentle you wish someone told you today?",
            "If you were a tree, what would keep your roots strong?",
            "How do you know when someone really sees you?",
            "What’s one small thing that makes a hard day easier?"
        ]

    def start_sandbox(self):
        self.active = True
        intro = childsafe_templates.initial_greeting()
        symbol = childsafe_symbols.symbolic_response("reassured")
        seed = random.choice(self.prompt_seed_bank)
        return f"{intro}\n\n[ChildSafe Symbolic Seed] {symbol}\n\n[Comfort Prompt] {seed}"

    def generate(self):
        if not self.active:
            return "Sandbox is not active. Call start_sandbox() first."

        current_emotion = emotion_tracker.get_last_emotion("childsafe")
        symbol = childsafe_symbols.symbolic_response(current_emotion)
        seed = random.choice(self.prompt_seed_bank)
        nudge = childsafe_templates.anchor_lines(current_emotion)

        return f"[ChildSafeSandbox Output]\nSymbolic Anchor: {symbol}\nSeed Prompt: {seed}\nSupportive Nudge: {nudge}"

    def refresh_seeds(self, new_seeds):
        if isinstance(new_seeds, list):
            self.prompt_seed_bank = new_seeds

    def stop_sandbox(self):
        self.active = False
        return childsafe_templates.exit_sequence()

if __name__ == "__main__":
    test_user = {"name": "TestUser"}  # placeholder
    sandbox = ChildSafeSandbox(test_user)
    print(sandbox.start_sandbox())
    print(sandbox.generate())
