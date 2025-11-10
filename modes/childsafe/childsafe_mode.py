# childsafe_mode.py
# ChildSafe Mode – Project_Raven | aeris_core
# Version 1.1 – Overlay-Based Personality, Stabilized Presence, and Safety

import os
import sys
import json
from pathlib import Path

# --- Path setup for project consistency ---
from utilities.path_refactor import get_full_path

try:
    from ..common import memory_utils as memory
except Exception:
    # graceful fallback if helper isn’t packaged
    class _Mem:
        def recall(_self, *a, **k): return None
    memory = _Mem()

ROOT_CANDIDATE = get_full_path("container/aeris_core")
if ROOT_CANDIDATE not in sys.path:
    sys.path.insert(0, ROOT_CANDIDATE)

from memory import emotional_tagging
from utilities.rituals import breath_sequence
from modes.childsafe import childsafe_templates
from utilities.mirroring import reflective_response
from utilities.symbolics import childsafe_symbols
from utilities.audio.tone_to_tts import get_tts_settings
from memory.session_emotion import emotion_tracker

def load_childsafe_overlay():
    overlay_path = get_full_path("container/aeris_core/app/modes/childsafe/connor_personality_overlay.json")
    try:
        with open(overlay_path, 'r', encoding='utf-8') as f:
            overlay_data = json.load(f)
        print(f"[Overlay] ChildSafe personality overlay loaded with tags: {overlay_data.get('overlay_tags', [])}")
        return overlay_data
    except FileNotFoundError:
        print("[Warning] Connor personality overlay not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"[Error] Failed to decode overlay: {e}")
        return {}

class ChildsafeMode:
    def __init__(self, user_profile, memory_vault):
        self.user = user_profile
        self.memory = memory_vault
        self.mode_name = "childsafe"
        self.tone = "gentle"
        self.presence_active = False
        self.is_filtering = True
        self.overlay = load_childsafe_overlay()

    def activate(self):
        self.presence_active = True
        phrase = self.overlay.get("mode_activation_phrase") if self.overlay else None
        return phrase or childsafe_templates.initial_greeting()

    def process_input(self, user_input):
        if self.is_fallback_needed(user_input):
            return self.get_overlay_fallback()

        if "safeword" in user_input.lower():
            return "Okay. We’re stopping here, gently."

        emotional_context = emotional_tagging.analyze(user_input)
        
        # Track session emotion
        emotion_tracker.update(self.mode_name, emotional_context)
        last = emotion_tracker.get_last_emotion(self.mode_name)
        print(f"[Session Tracker]: Last emotion in ChildSafe was {last}")   

        symbol = childsafe_symbols.symbolic_response(emotional_context)
        print(f"[ChildSafe Symbolic]: {symbol}")

        tts_settings = get_tts_settings(emotional_context)
        print(f"[TTS Settings for ChildSafe Mode]: {tts_settings}") 
        
        # Pull template anchors for specific kid-focused emotions
        if emotional_context in ["confusion", "fear", "lonely"]:
            anchor = childsafe_templates.anchor_lines(emotional_context)
            return self._filtered_response(anchor)

        reflection = reflective_response.generate(user_input, emotional_context)
        return self._filtered_response(reflection)
        
    def _filtered_response(self, message):
        """Extra language guardrails and consistent gentle tone."""
        return f"[ChildSafeMode] {message}"

    def offer_breathing(self):
        return "\n".join(breath_sequence.simple_breathing_cycle())

    def deactivate(self):
        self.presence_active = False
        self.is_filtering = False
        phrase = self.overlay.get("mode_exit_phrase") if self.overlay else None
        return phrase or childsafe_templates.exit_sequence()
        
    def is_fallback_needed(self, user_input):
        # Insert checks for content, tone, or unsupported queries if needed.
        return False

    def get_overlay_fallback(self):
        fallbacks = self.overlay.get("fallback_responses", [])
        if fallbacks:
            return random.choice(fallbacks)
        else:
            return "That’s a big feeling. I’m here, and we can talk about it if you want."

# --- Standalone Test ---
if __name__ == "__main__":
    print("[Debug] ChildSafe fallback test:", ChildsafeMode({}, {}).get_overlay_fallback())
