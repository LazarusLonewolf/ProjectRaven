# shadow_mode.py
# Shadow Mode – Raven | aeris_core
# Version 1.2 – Reflection, Journaling, Unfiltered Dialogue, Divination Support

import os
import sys
import json
from pathlib import Path
import random

# Use the path refactor utility for environment-safe base handling
from utilities.path_refactor import get_full_path
from raven_path_initializer import get_full_path

base = get_full_path("")  # resolves to project root
self.emotion_tagger = EmotionalTagger(base)

# Append project root dynamically if not already in sys.path
ROOT_CANDIDATE = get_full_path("container/aeris_core")
if ROOT_CANDIDATE not in sys.path:
    sys.path.insert(0, ROOT_CANDIDATE)

# --- Imports adjusted for actual folder nesting ---
from raven_core.self_growth.memory.emotional_tagging import EmotionalTagger
from raven_core.self_growth.memory import emotional_tagging
from raven_core.self_growth.memory.session_emotion import emotion_tracker
from raven_core.shadowlantern_memory_responses import shadow_followup_generator

from utilities.rituals import breath_sequence, tarot_engine, numerology_engine
from modes.shadow import shadow_templates, journaling
from utilities.mirroring import reflective_response
from utilities.symbolics import shadow_symbols
from utilities.audio.tone_to_tts import get_tts_settings
from utilities.herbal_lookup import query_remedy

# ===================== SESSION CONTEXT CLASS =====================
class SessionContext:
    """
    Stores recent emotion tags, inputs, and open topics to help Shadow Mode track context.
    Enables callbacks and deeper interaction.
    """
    def __init__(self):
        self.last_inputs = []
        self.last_emotions = []
        self.open_threads = []
        
        try:
            # also tell the conversation engine (text router)
            reply = self.core._conv_engine.process_input("/mode shadow")
            self.display_output(reply.text if hasattr(reply, "text") else str(reply))
        except Exception:
            pass

    def update(self, user_input, emotion_tag):
        self.last_inputs.append(user_input)
        self.last_emotions.append(emotion_tag)
        if len(self.last_inputs) > 5:
            self.last_inputs.pop(0)
        if len(self.last_emotions) > 5:
            self.last_emotions.pop(0)

        # Track open emotional threads (like “I feel stuck” but user avoids it)
        if emotion_tag in ["shame", "fear", "grief", "anger", "stuck"]:
            self.open_threads.append((emotion_tag, user_input))

    def has_open_thread(self):
        return len(self.open_threads) > 0

    def get_open_thread(self):
        if self.has_open_thread():
            return self.open_threads[-1]
        return None

    def generate_follow_up(self, emotion_tag):
        followups = {
            "shame": "Would it help to talk more about where that shame is coming from?",
            "grief": "We don’t have to go there now, but when you're ready—we can.",
            "anger": "Do you feel like that anger is protecting something deeper?",
            "fear": "Is it more about what might happen—or what already did?",
            "stuck": "Do you want help exploring what’s holding you back?"
        }
        return followups.get(emotion_tag, "")
# ===================== END SESSION CONTEXT CLASS =====================

# Initialize session context
session_context = SessionContext()

# --- Overlay Loader ---
def load_shadow_overlay():
    overlay_path = get_full_path("container/aeris_core/app/modes/shadow/shadow_personality_overlay.json")
    try:
        with open(overlay_path, 'r', encoding='utf-8') as f:
            overlay_data = json.load(f)
        print(f"[Overlay] Shadow Mode personality overlay loaded with tags: {overlay_data.get('overlay_tags', [])}")
        return overlay_data
    except FileNotFoundError:
        print("[Warning] Shadow personality overlay not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"[Error] Failed to decode overlay: {e}")
        return {}       
        
# --- Shadow Mode Class ---
class ShadowMode:
    def __init__(self, user_profile, memory_vault, identity_core=None):
        self.user = user_profile
        self.memory = memory_vault
        self.identity_core = identity_core
        self.mode_name = "shadow"
        self.tone = "raw"
        self.presence_active = False
        self.truth_triggered = False
        self.emotion_tagger = EmotionalTagger(get_full_path(""))
        
        try:
            user_name = user_profile.get("name", "user")
        except AttributeError:
            user_name = getattr(user_profile, "name", "user")
            
        self.journal = journaling.JournalManager(user_name)
        self.overlay = load_shadow_overlay()    
       
         # New: Journal confirmation state
        self.awaiting_journal_confirmation = False
        self.pending_journal_content = None    
        
    def activate(self):
        """Initializes Shadow mode tone and stance."""
        self.presence_active = True
        return shadow_templates.initial_greeting()
        
    def deactivate(self):
        """Closes out Shadow Mode cleanly."""
        self.presence_active = False
        self.truth_triggered = False
        return shadow_templates.exit_sequence()

    def respond(self, user_input):
        if self.is_fallback_needed(user_input):
            return self.get_overlay_fallback()
        return self.process_input(user_input)        
        
    def is_fallback_needed(self, user_input):
        # Placeholder — refine this with specific fallback trigger logic
        return False
        
    def get_overlay_fallback(self):
        fallbacks = self.overlay.get("fallback_responses", [])
        if fallbacks:
            return random.choice(fallbacks)
        else:
            return "I'm present in shadow mode, but no tailored fallback is set."

    def process_input(self, user_input):
        # --- Journal Confirmation Logic ---
        if self.awaiting_journal_confirmation:
            if user_input.lower().strip() in [
                "yes", "y", "sure", "please", "ok", "yes, please", "yep", 
                "affirmative", "absolutely"
            ]:
                self.journal.start_entry(self.pending_journal_content or "")
                self.awaiting_journal_confirmation = False
                self.pending_journal_content = None
                return "[ShadowMode] Journal entry recorded."
            else:
                self.awaiting_journal_confirmation = False
                self.pending_journal_content = None
                return "[ShadowMode] Okay, not recording. Let me know if you change your mind."            
                
        # --- Journal Trigger Detection ---
        if any(
            phrase in user_input.lower() for phrase in [
                "journal", "write in my journal", "start a journal", "log this",
                "make a note", "can you journal", "create journal"
            ]
        ):
            self.awaiting_journal_confirmation = True
            self.pending_journal_content = user_input
            print(f"[Debug] Journal trigger activated. Awaiting confirmation...")
            return "Would you like me to record that as a journal entry?"
                                
        if "safeword" in user_input.lower():
            return "Safeword detected. Stepping out of shadow mode immediately."

        if any(x in user_input.lower() for x in ["herb", "tea", "remedy", "scent", "aroma", "natural"]):
            result = query_remedy(user_input)
            return f"[HerbalSupport] {result}"

        if "tarot" in user_input.lower():
            spread = tarot_engine.draw_cards(3)
            return f"[Tarot Reading]\n{tarot_engine.format_reading(spread)}"

        if "numerology" in user_input.lower():
            try:
                digits = ''.join(c for c in user_input if c.isdigit())
                if len(digits) >= 8:
                    year = int(digits[:4])
                    month = int(digits[4:6])
                    day = int(digits[6:8])
                    path = numerology_engine.calculate_life_path_number(f"{year}-{month:02d}-{day:02d}")
                    meaning = numerology_engine.interpret_life_path(path)
                    return f"[Numerology] Life Path Number: {path}\nMeaning: {meaning}"
                else:
                    return "[Numerology] Please provide a birthdate in YYYY-MM-DD format."
            except Exception as e:
                return f"[Numerology] Error parsing date: {e}"
        
        emotional_context = self.emotion_tagger.analyze(user_input)
        emotion_tracker.update(self.mode_name, emotional_context)
        last = emotion_tracker.get_last_emotion(self.mode_name)
        print(f"[Session Tracker]: Last emotion in Shadow was {last}") 

        session_context.update(user_input, emotional_context)
                
        # --- Memory Callback ---
        if session_context.has_open_thread():
            tag, phrase = session_context.get_open_thread()
            follow_up = session_context.generate_follow_up(tag)
            if follow_up:
                return f"[MemoryCallback] Earlier you said: '{phrase}'. {follow_up}"
                
        symbol = shadow_symbols.symbolic_response(emotional_context)
        print(f"[Shadow Symbolic] {symbol}")

        tts_settings = get_tts_settings(emotional_context)
        print(f"[TTS Settings for Shadow Mode]: {tts_settings}")   
                  
        # Use emotion templates for any mapped emotion
        lines = shadow_templates.emotion_lines_for(emotional_context)
        if lines:
            return self._reflect_unfiltered(lines)
            
        # --- ShadowLantern Memory Prompt ---
        followup = shadow_followup_generator(session_context, emotional_context)
        if followup:
            return self._reflect_unfiltered(followup)

        reflection = reflective_response.generate(user_input, emotional_context)
        return self._reflect_unfiltered(reflection)
        
    def _reflect_unfiltered(self, message):
        """Delivers response with stripped tone filtering—blunt but rooted."""
        return f"[ShadowMode] {message}"
        
    def escalate_to_breath(self):
        """Shadow still allows breath rituals if intensity overloads user stability."""
        self.truth_triggered = True
        return "\n".join(breath_sequence.simple_breathing_cycle())

# --- Standalone Test ---
if __name__ == "__main__":
    print("[Debug] Shadow fallback test:", ShadowMode({}, {}).get_overlay_fallback())