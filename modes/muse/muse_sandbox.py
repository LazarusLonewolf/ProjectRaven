
# muse_sandbox.py – Final Hybrid Muse Sandbox
# Combines emotional context, symbolic hooks, seed prompts, and sandbox lifecycle management

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import random
from utilities.symbolics import muse_symbols
from modes.muse import muse_templates
from memory.session_emotion import emotion_tracker

class MuseSandbox:
    def __init__(self, user_profile):
        self.user = user_profile
        self.active = False
        self.prompt_seed_bank = [
            "What if your thoughts had weather patterns?",
            "Imagine a color that feels like nostalgia.",
            "What does silence sound like in your favorite place?",
            "Describe a memory with the wrong emotion on purpose.",
            "Invent a constellation based on your week.",
            "What if clouds could remember us?",
            "How would you draw silence?",
            "Imagine a door that leads to nowhere.",
            "What color is a forgotten memory?",
            "If your thoughts were rooms, what would they look like?",
            "Where does a question go when it's unanswered?"
        ]

    def start_sandbox(self):
        self.active = True
        intro = muse_templates.initial_greeting()
        symbol = muse_symbols.symbolic_response("curious")
        seed = random.choice(self.prompt_seed_bank)
        return f"{intro}\n\n[Muse Symbolic Seed] {symbol}\n\n[Creative Prompt] {seed}"

    def generate(self):
        if not self.active:
            return "Sandbox is not active. Call start_sandbox() first."

        current_emotion = emotion_tracker.get_last_emotion("muse")
        symbol = muse_symbols.symbolic_response(current_emotion)
        seed = random.choice(self.prompt_seed_bank)
        lateral_nudge = muse_templates.anchor_lines(current_emotion)

        return f"[MuseSandbox Output]\nSymbolic Hook: {symbol}\nSeed Prompt: {seed}\nCreative Nudge: {lateral_nudge}"

    def refresh_seeds(self, new_seeds):
        if isinstance(new_seeds, list):
            self.prompt_seed_bank = new_seeds

    def stop_sandbox(self):
        self.active = False
        return muse_templates.exit_sequence()
        
if __name__ == "__main__":
    test_user = {"name": "TestUser"}  # placeholder
    sandbox = MuseSandbox(test_user)
    print(sandbox.start_sandbox())   # <-- initializes and prints intro + first seed
    print(sandbox.generate())        # <-- follow-up output
