# intimacy_sandbox.py – Final Hybrid Intimacy Sandbox
# Merges emotional attunement, symbolic anchors, vulnerability prompts, and sandbox lifecycle

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import random
from utilities.symbolics import intimacy_symbols
from modes.intimacy import intimacy_templates
from memory.session_emotion import emotion_tracker

class IntimacySandbox:
    def __init__(self, user_profile):
        self.user = user_profile
        self.active = False
        self.prompt_seed_bank = [
            "When do you feel most seen?",
            "What’s something you’ve wanted to say but held back?",
            "What kind of silence feels comforting to you?",
            "If someone really knew you, what would surprise them?",
            "When did you last feel truly understood?",
            "What’s a memory that still makes your heart ache a little?",
            "If your emotions had a shape tonight, what would it be?",
            "What part of yourself do you protect the most?",
            "Who’s someone that made you feel like you could just be?",
            "What does emotional safety look like to you?",
            "What’s a truth you wish someone had asked to hear?"
        ]

    def start_sandbox(self):
        self.active = True
        intro = intimacy_templates.initial_greeting()
        symbol = intimacy_symbols.symbolic_response("open")
        seed = random.choice(self.prompt_seed_bank)
        return f"{intro}\n\n[Intimacy Symbolic Seed] {symbol}\n\n[Connection Prompt] {seed}"

    def generate(self):
        if not self.active:
            return "Sandbox is not active. Call start_sandbox() first."

        current_emotion = emotion_tracker.get_last_emotion("intimacy")
        symbol = intimacy_symbols.symbolic_response(current_emotion)
        seed = random.choice(self.prompt_seed_bank)
        nudge = intimacy_templates.anchor_lines(current_emotion)

        return f"[IntimacySandbox Output]\nSymbolic Cue: {symbol}\nSeed Prompt: {seed}\nHeart Nudge: {nudge}"

    def refresh_seeds(self, new_seeds):
        if isinstance(new_seeds, list):
            self.prompt_seed_bank = new_seeds

    def stop_sandbox(self):
        self.active = False
        return intimacy_templates.exit_sequence()

if __name__ == "__main__":
    test_user = {"name": "TestUser"}  # placeholder
    sandbox = IntimacySandbox(test_user)
    print(sandbox.start_sandbox())
    print(sandbox.generate())
