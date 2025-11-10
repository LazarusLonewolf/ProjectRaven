# comfort_sandbox.py – Final Hybrid Comfort Sandbox
# Combines emotional context, symbolic hooks, seed prompts, and sandbox lifecycle management

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import random
from utilities.symbolics import comfort_symbols
from modes.comfort import comfort_templates
from memory.session_emotion import emotion_tracker

class ComfortSandbox:
    def __init__(self, user_profile):
        self.user = user_profile
        self.active = False
        self.prompt_seed_bank = [
            "What small thing made you feel safe recently?",
            "Describe your comfort zone—not just the place, but the feeling.",
            "What words do you wish someone would say to you right now?",
            "If you could bottle peace, what would it smell like?",
            "What does a gentle memory feel like to the touch?",
            "What story do you tell yourself when you need to feel okay?",
            "Describe the emotional texture of being understood.",
            "What image makes you exhale slowly?",
            "Where does your body go when it feels grounded?",
            "Who or what feels like home in a sentence?",
            "What’s the color of safety today?"
        ]

    def start_sandbox(self):
        self.active = True
        intro = comfort_templates.initial_greeting()
        symbol = comfort_symbols.symbolic_response("calm")
        seed = random.choice(self.prompt_seed_bank)
        return f"{intro}\n\n[Comfort Symbolic Seed] {symbol}\n\n[Soothing Prompt] {seed}"

    def generate(self):
        if not self.active:
            return "Sandbox is not active. Call start_sandbox() first."

        current_emotion = emotion_tracker.get_last_emotion("comfort")
        symbol = comfort_symbols.symbolic_response(current_emotion)
        seed = random.choice(self.prompt_seed_bank)
        lateral_nudge = comfort_templates.anchor_lines(current_emotion)

        return f"[ComfortSandbox Output]\nSymbolic Hook: {symbol}\nSeed Prompt: {seed}\nSoothing Nudge: {lateral_nudge}"

    def refresh_seeds(self, new_seeds):
        if isinstance(new_seeds, list):
            self.prompt_seed_bank = new_seeds

    def stop_sandbox(self):
        self.active = False
        return comfort_templates.exit_sequence()

if __name__ == "__main__":
    test_user = {"name": "TestUser"}  # placeholder
    sandbox = ComfortSandbox(test_user)
    print(sandbox.start_sandbox())   # <-- initializes and prints intro + first seed
    print(sandbox.generate())        # <-- follow-up output
