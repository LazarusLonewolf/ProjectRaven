# intimacy_mode.py
# Intimacy Mode – Project_Raven | aeris_core
# Version 1.0 – Soft Vulnerability & Gated Emotional Depth
# Aliases: "intimacy_mode", "flamekeeper_mode", "flamekeeper"

import os
import sys
import json
from pathlib import Path

from utilities.path_refactor import get_full_path

ROOT_CANDIDATE = get_full_path("container/aeris_core")
if ROOT_CANDIDATE not in sys.path:
    sys.path.insert(0, ROOT_CANDIDATE)

# Mode aliases for clarity in logs/conversation
MODE_NAME = "intimacy"
FLAMEKEEPER_NAME = "flamekeeper"
FLAMEKEEPER_MODE = "flamekeeper_mode"

TEMPLATE_PATH = get_full_path("container/aeris_core/app/modes/intimacy/intimacy_templates.json")

from raven_core.self_growth.memory import emotional_tagging
from raven_core.self_growth.memory.session_emotion import emotion_tracker
from utilities.rituals import breath_sequence
from modes.intimacy import intimacy_templates
from utilities.mirroring import reflective_response
from utilities.symbolics import intimacy_symbols
from utilities.audio.tone_to_tts import get_tts_settings
from raven_core.vault_interface import list_vault_files, read_vault_file, search_vault
from raven_core.consent_gate import verify_consent

class IntimacyMode:
    OVERLAY_PATH = get_full_path("container/aeris_core/app/modes/intimacy/intimacy_personality_overlay.json")
    
    def __init__(self, user_profile, memory_vault):
        self.user = user_profile
        self.memory = memory_vault
        self.mode_name = "intimacy"
        self.tone = "warm"
        self.presence_active = False
        self.safe_opening = False
        self.consent_verified = False
        self.overlay_loaded = False
        self.overlay_tags = []
    
    def load_overlay(self):
        try:
            with open(self.OVERLAY_PATH, 'r', encoding='utf-8') as f:
                overlay_data = json.load(f)
                self.overlay_tags = overlay_data.get("overlay_tags", [])
                self.overlay_loaded = True
                print(f"[Overlay] Flamekeeper overlay loaded with tags: {self.overlay_tags}")
                return "[Flamekeeper] Emotional overlay initialized."
        except FileNotFoundError:
            print("[Warning] Flamekeeper overlay not found. Proceeding without overlays.")
            return "[Flamekeeper] Overlay not found. Using default tone."
        except json.JSONDecodeError as e:
            print(f"[Error] Overlay JSON decode error: {e}")
            return "[Flamekeeper] Error loading overlay content."

    def activate(self):
        if not self.consent_verified:
            is_allowed, reason = verify_consent(self.user)
            if not is_allowed:
                return f"[IntimacyMode] {reason}"
            self.consent_verified = True
        self.presence_active = True
        self.load_overlay()
        return intimacy_templates.initial_greeting()

    def process_input(self, user_input):
        """Processes input for deeper presence and soft vulnerability."""
        if "safeword" in user_input.lower():
            return "Safeword detected. Re-centering and disengaging intimacy tone."

        emotional_context = emotional_tagging.analyze(user_input)
        emotion_tracker.update(self.mode_name, emotional_context)
        last = emotion_tracker.get_last_emotion(self.mode_name)
        print(f"[Session Tracker]: Last emotion in Intimacy was {last}")

        symbol = intimacy_symbols.symbolic_response(emotional_context)
        print(f"[Intimacy Symbolic]: {symbol}")

        tts_settings = get_tts_settings(emotional_context)
        print(f"[TTS Settings for Intimacy Mode]: {tts_settings}")

        if emotional_context in ["shame", "withdrawal", "silence"]:
            anchor = intimacy_templates.anchor_lines(emotional_context)
            return self._soft_reflection(anchor)

        reflection = reflective_response.generate(user_input, emotional_context)
        return self._soft_reflection(reflection)

    def respond(self, user_input):
        if not self.consent_verified:
            return "[Flamekeeper] Consent not yet confirmed. Access restricted."

        # Example custom phrasing for typical requests
        if "hold me" in user_input.lower():
            return "[Flamekeeper] I'm right here. You’re not alone. Do you want to describe what you’re feeling?"
        if "touch" in user_input.lower():
            return "[Flamekeeper] Only if you want that, and only where it feels safe. You choose. No pressure."

        # Default response
        return "[Flamekeeper] I hear you. Intimacy begins with honesty. What do you need from me right now?"

    def _soft_reflection(self, message):
        """Applies intimacy tone overlays—soft, affirming, emotionally open."""
        return f"[IntimacyMode] {message}"

    def escalate_to_breath(self):
        """Optional breath ritual if emotional overwhelm is detected."""
        self.safe_opening = True
        return "\n".join(breath_sequence.simple_breathing_cycle())

    def deactivate(self):
        self.consent_verified = False
        self.presence_active = False
        return "[Flamekeeper] Mode exit complete."

# Optional test
if __name__ == "__main__":
    fake_user = {"name": "Casey"}
    flame = IntimacyMode(fake_user, memory_vault={})
    print(flame.activate())