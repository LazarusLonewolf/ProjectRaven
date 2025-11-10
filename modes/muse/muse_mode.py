# muse_mode.py
# Muse Mode – Raven | aeris_core
# Version 1.0 – Creative Reflection & Lateral Inquiry Layer

import os
import sys
import json
from pathlib import Path
import random

# Use the path refactor utility for environment-safe base handling
from utilities.path_refactor import get_full_path

try:
    from project_progress_tracker import (
        load_project_map,
        summarize_progress,
        next_actions_for_track,
    )
except Exception:
    # keep mode loadable even if the helper isn't present
    def load_project_map(*_a, **_k): return {}
    def summarize_progress(*_a, **_k): return "No tracker available."
    def next_actions_for_track(*_a, **_k): return []
    
# Append project root dynamically if not already in sys.path
ROOT_CANDIDATE = get_full_path("container/aeris_core")
if ROOT_CANDIDATE not in sys.path:
    sys.path.insert(0, ROOT_CANDIDATE)

# Add DevTools folder to sys.path dynamically
devtools_path = get_full_path("devtools")
if devtools_path not in sys.path:
    sys.path.append(devtools_path)

# Import the unified Game Framework
from game_framework import (
    TemplateLibrary,
    create_project_skeleton,
    sample_templates,
    detect_game_language,
)


# Import DevTools modules (functions) with safe names
from guided_creator import start_guided_creation

from project_ideation_engine import (
    gather_project_goals,
    suggest_languages,
    summarize_and_recommend,
)

    from project_progress_tracker import (
        log_project_progress,
        get_latest_entries,
        update_project_status,
        load_projects as load_progress_projects,  # avoid name clash
    )

from project_resume_handler import (
    load_projects as load_resume_projects,     # avoid name clash
    list_active_projects,
)
# --- Imports adjusted for actual folder nesting ---
from raven_core.self_growth.memory.emotional_tagging import EmotionalTagger
from raven_core.self_growth.memory.session_emotion import emotion_tracker

from utilities.rituals import breath_sequence
from modes.muse import muse_templates
from utilities.mirroring import reflective_response
from utilities.symbolics import muse_symbols
from utilities.audio.tone_to_tts import get_tts_settings

# Import other DevTools modules as needed
from guided_creator import GuidedCreator
from project_ideation_engine import ProjectIdeationEngine
from project_progress_tracker import ProjectProgressTracker
from project_resume_handler import load_projects, list_active_projects

def load_muse_overlay():
    overlay_path = get_full_path("container/aeris_core/app/modes/muse/muse_personality_overlay.json")
    try:
        with open(overlay_path, 'r', encoding='utf-8') as f:
            overlay_data = json.load(f)
        print(f"[Overlay] Muse Mode personality overlay loaded with tags: {overlay_data.get('overlay_tags', [])}")
        return overlay_data
    except FileNotFoundError:
        print("[Warning] Muse personality overlay not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"[Error] Failed to decode overlay: {e}")
        return {}

class MuseMode:
    def __init__(self, user_profile, memory_vault, identity_core=None):
        self.user = user_profile
        self.memory = memory_vault
        self.identity_core = identity_core
        self.mode_name = "muse"
        self.presence_active = False
        self.emotion_tagger = EmotionalTagger(get_full_path(""))
        self.overlay = load_muse_overlay()
        self.tone = "curious"
        self.flow_active = False
        
    # === DevTools Command Helpers (Muse) ===================================
    def _cmd_help(self):
        return (
            "[Muse/DevTools]\n"
            "Commands:\n"
            "  muse help                       -> this menu\n"
            "  muse ideate                     -> guided Q&A; recommends engines\n"
            "  muse scaffold language <dest> <language> [title]\n"
            "                                  -> create language-first scaffold\n"
            "  muse scaffold template <name> <dest>\n"
            "                                  -> create template skeleton\n"
            "  muse guided create              -> run guided creator walkthrough\n"
            "  muse progress update <project> <status> [notes]\n"
            "  muse progress show [n]          -> show last n log rows (default 5)\n"
            "  muse projects active            -> list active projects (resume DB)\n"
        )

    def _cmd_ideate(self):
        info = {}
        try:
            info = {
                "goal": input("Goal (platformer/story/puzzle/etc): ").strip(),
                "audience": input("Audience (kids/teens/adults/edu): ").strip(),
                "style": input("Style (pixel/noir/fantasy/etc): ").strip(),
                "platform": input("Platform (PC/Android/iOS/Web): ").strip(),
            }
        except EOFError:
            return "[Muse] Input aborted."

        langs = suggest_languages(info)
        summarize_and_recommend(info, langs)
        return "[Muse] Ideation summary printed above."

    def _cmd_scaffold_language(self, args):
        # muse scaffold language <dest> <language> [title]
        if len(args) < 3:
            return "[Muse] Usage: muse scaffold language <dest> <language> [title]"
        dest, language = args[1], args[2]
        title = args[3] if len(args) > 3 else None
        try:
            created_path = create_project_skeleton(dest, language, title)
            return f"[Muse] Language scaffold created at: {created_path}"
        except Exception as e:
            return f"[Muse] Scaffold error: {e}"

    def _cmd_scaffold_template(self, args):
        # muse scaffold template <name> <dest>
        if len(args) < 3:
            return "[Muse] Usage: muse scaffold template <name> <dest>"
        name, dest = args[1], args[2]
        lib = TemplateLibrary()
        result = create_project_skeleton(name, lib, dest)
        return f"[Muse] {result}"

    def _cmd_guided_create(self):
        try:
            start_guided_creation()
            return "[Muse] Guided creator completed."
        except Exception as e:
            return f"[Muse] Guided creator error: {e}"

    def _cmd_progress_update(self, args):
        # muse progress update <project> <status> [notes...]
        if len(args) < 3:
            return "[Muse] Usage: muse progress update <project> <status> [notes]"
        project, status = args[1], args[2]
        notes = " ".join(args[3:]) if len(args) > 3 else ""
        try:
            csv_path = log_project_progress(project, status, notes)
            update_project_status(project, status)
            return f"[Muse] Progress logged. CSV: {csv_path}"
        except Exception as e:
            return f"[Muse] Progress update error: {e}"

    def _cmd_progress_show(self, args):
        # muse progress show [n]
        n = 5
        if len(args) >= 2:
            try:
                n = int(args[1])
            except ValueError:
                return "[Muse] Usage: muse progress show [n]"
        rows = get_latest_entries(limit=n)
        if not rows:
            return "[Muse] No progress log yet."
        return "[Muse] Recent progress:\n" + "".join(rows)

    def _cmd_projects_active(self):
        try:
            active = list_active_projects()
            if not active:
                return "[Muse] No active projects."
            names = [p.get("name", "<unnamed>") for p in active]
            return "[Muse] Active projects:\n- " + "\n- ".join(names)
        except Exception as e:
            return f"[Muse] Could not load active projects: {e}"

    def activate(self):
        """Engages Muse Mode—light, curious, playful tone."""
        self.presence_active = True
        return muse_templates.initial_greeting()

    def process_input(self, user_input):
        """Processes input with generative thinking and tangents."""
        text = (user_input or "").strip()
        lower = text.lower()
        
        if lower.startswith("muse "):
           parts = text.split()
           if len(parts) >= 2:
                cmd = parts[1]
                args = parts[1:]  # includes the command keyword
                if cmd == "help":
                    return self._cmd_help()
                if cmd == "ideate":
                    return self._cmd_ideate()
                if cmd == "scaffold" and len(args) >= 2:
                    # muse scaffold language ... | muse scaffold template ...
                    sub = args[1]
                    if sub == "language":
                        return self._cmd_scaffold_language(args)
                    if sub == "template":
                        return self._cmd_scaffold_template(args)
                    return "[Muse] Usage: muse scaffold [language|template] ..."
                if cmd == "guided" and len(args) >= 2 and args[1] == "create":
                    return self._cmd_guided_create()
                if cmd == "progress" and len(args) >= 2:
                    sub = args[1]
                    if sub == "update":
                        return self._cmd_progress_update(args)
                    if sub == "show":
                        return self._cmd_progress_show(args[1:])
                    return "[Muse] Usage: muse progress [update|show] ..."
                if cmd == "projects" and len(args) >= 2 and args[1] == "active":
                    return self._cmd_projects_active()
                return "[Muse] Unknown command. Try: muse help"
                
        # --- fall through to existing Muse behavior below ---
        if self.is_fallback_needed(user_input):
            return self.get_overlay_fallback()
            
        if "sacred stop" in user_input.lower():
            return "Muse pausing. No worries. We can stop here."

        emotional_context = emotional_tagging.analyze(user_input)
        
        # Track session emotion
        emotion_tracker.update(self.mode_name, emotional_context)
        last = emotion_tracker.get_last_emotion(self.mode_name)
        print(f"[Session Tracker]: Last emotion in Muse was {last}")
        
        symbol = muse_symbols.symbolic_response(emotional_context)
        print(f"[Muse Symbolic] {symbol}")    
        
        # Tone-to-TTS mapping
        tts_settings = get_tts_settings(emotional_context)
        print(f"[TTS Settings for Muse Mode]: {tts_settings}")  

        if emotional_context in ["bored", "inspired", "curious"]:
            anchor = muse_templates.anchor_lines(emotional_context)
            return self._creative_return(anchor)

        reflection = reflective_response.generate(user_input, emotional_context)
        return self._creative_return(reflection)

    def _creative_return(self, message):
        """Delivers whimsical or sideways insight."""
        return f"[MuseMode] {message}"

    def escalate_to_breath(self):
        """Optional grounding if user gets overwhelmed mid-flow."""
        self.flow_active = True
        return "\n".join(breath_sequence.simple_breathing_cycle())

    def deactivate(self):
        """Exits Muse mode gently."""
        self.presence_active = False
        self.flow_active = False
        return muse_templates.exit_sequence()
        
    def is_fallback_needed(self, user_input):
        # Placeholder: can refine this later for advanced edge-case triggers
        return False

    def get_overlay_fallback(self):
        fallbacks = self.overlay.get("fallback_responses", [])
        if fallbacks:
            return random.choice(fallbacks)
        else:
            return "Muse Mode is listening, but I don’t have a quirky answer for that… yet."

