# shadow_sandbox.py – Final Hybrid Shadow Sandbox
# Combines emotional depth, symbolic anchors, reflection seeds, and sandbox lifecycle

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import random
from utilities.symbolics import shadow_symbols
from modes.shadow import shadow_templates
from memory.session_emotion import emotion_tracker

class ShadowSandbox:
    def __init__(self, user_profile):
        self.user = user_profile
        self.active = False
        self.prompt_seed_bank = [
            "What part of your truth have you avoided today?",
            "What emotion is hardest for you to name?",
            "When did silence feel loudest?",
            "Describe the shape of a regret.",
            "What mask are you wearing right now?",
            "What belief are you still holding that no longer serves you?",
            "If your shadow could speak, what would it say?",
            "What part of yourself do you still keep in the dark?",
            "What fear disguises itself as strength?",
            "Who are you when no one is watching?",
            "What truth keeps trying to surface?"
        ]

    def start_sandbox(self):
        self.active = True
        intro = shadow_templates.initial_greeting()
        symbol = shadow_symbols.symbolic_response("reflective")
        seed = random.choice(self.prompt_seed_bank)
        return f"{intro}\n\n[Shadow Symbolic Seed] {symbol}\n\n[Reflection Prompt] {seed}"

    def generate(self):
        if not self.active:
            return "Sandbox is not active. Call start_sandbox() first."

        current_emotion = emotion_tracker.get_last_emotion("shadow")
        symbol = shadow_symbols.symbolic_response(current_emotion)
        seed = random.choice(self.prompt_seed_bank)
        nudge = shadow_templates.anchor_lines(current_emotion)

        return f"[ShadowSandbox Output]\nSymbolic Anchor: {symbol}\nSeed Prompt: {seed}\nReflective Nudge: {nudge}"

    def refresh_seeds(self, new_seeds):
        if isinstance(new_seeds, list):
            self.prompt_seed_bank = new_seeds

    def stop_sandbox(self):
        self.active = False
        return shadow_templates.exit_sequence()
        
if __name__ == "__main__":
    test_user = {"name": "TestUser"}  # placeholder
    sandbox = ShadowSandbox(test_user)
    print(sandbox.start_sandbox())
    print(sandbox.generate())
