# Raven/raven_core/conversation_engine.py
# Lightweight-but-robust conversation engine for Raven
# - Always-on pre-pass before modes
# - Local-first, no cloud calls
# - Uses real EmotionalTagger if available; safe fallbacks otherwise
# - Optional overlay lookups
# - Optional dynamic_response hook
# - Deterministic outputs for testing

from __future__ import annotations

import json
import sys
import os
import time
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple

# Prefer the real mirroring helper (GUI sets these paths); safe fallback otherwise
try:
    from utilities.mirroring import reflective_response as mirror
except Exception:
    class _MirrorFallback:
        @staticmethod
        def generate(user: str, emo: str) -> str:
            # Minimal stand-in: just echo user with a gentle confirmation.
            user = (user or "").strip()
            if not user:
                return "I’m here. What’s on your mind?"
            return user  # keep deterministic for tests
    mirror = _MirrorFallback()

try:
    from raven_core.llm_client import LLMClient, LLMConfig
    from raven_core.prompt_builder import build_chat_messages
except Exception:
    LLMClient = LLMConfig = build_chat_messages = None
    
from raven_core.intent_loader import detect_intent

JOURNAL_DIR = Path(__file__).resolve().parent / "self_growth" / "journals" / "reflection" / "reflections"
JOURNAL_DIR.mkdir(parents=True, exist_ok=True)

try:
    from utilities.rituals.tarot_engine import draw_spread, format_reading
except Exception:
    draw_spread = format_reading = None

try:
    from utilities.rituals.numerology_engine import calculate_life_path_number, interpret_life_path
except Exception:
    calculate_life_path_number = interpret_life_path = None

# ---- Try Raven's real tagger; fallback to a simple stub if missing ----
try:
    from raven_core.self_growth.memory.emotional_tagging import EmotionalTagger  # real path (yours)
except Exception:
    class EmotionalTagger:  # minimal stub
        @staticmethod
        def analyze(text: str) -> str:
            t = (text or "").lower()
            if any(k in t for k in ("overwhelm", "tired", "can't focus", "anxious", "sad", "down")):
                return "overwhelm"
            if any(k in t for k in ("angry", "mad", "frustrat")):
                return "frustration"
            if any(k in t for k in ("idea", "story", "create", "brainstorm")):
                return "curious"
            return "neutral"

# ---- Optional dynamic response hook (safe import) ----
_dynamic_generate = None
try:
    from raven_core.raven_dynamic_response import generate_response as _dynamic_generate  # <- note filename
except Exception:
    _dynamic_generate = None

# ---- Minimal session state for continuity (no persistence in v1) ----
class SessionState:
    def __init__(self, window: int = 6):
        self.last_emotion: str = "neutral"
        self.pending_flags: set[str] = set()
        self.context_window: List[Tuple[str, str]] = []
        self.max_window = max(2, int(window))

    def update_emotion(self, e: str) -> None:
        if e:
            self.last_emotion = e

    def add_pair(self, user: str, ai: str) -> None:
        self.context_window.append((user, ai))
        if len(self.context_window) > self.max_window:
            self.context_window.pop(0)

    def set_pending(self, flag: str) -> None:
        self.pending_flags.add(flag)

    def clear_pending(self, flag: str) -> None:
        self.pending_flags.discard(flag)

# ---- Simple template bank; overlays can override per-emotion lines ----
class TemplateBank:      
    _BANK = {
        "overwhelm": [
            "You don’t have to hold everything at once. Want a 60‑second reset or one small next step?",
            "Let me shoulder some of it. Name one thing and I’ll break it down."
        ],
        "frustration": [
            "I hear the friction. Want a quick triage: block, risk, next move?",
            "Okay—what’s the smallest piece we can win in 5 minutes?"
        ],
        "curious": [
            "Let’s pull that thread. What detail feels brightest right now?",
            "Prototype time: two constraints and one wild card—ready?"
        ],
        "neutral": [
            "I’m with you. Tell me more or say ‘help’ for options.",
            "Got it. Do you want ideas, a plan, or just space?"
        ],
    }

    @classmethod
    def get_line(cls, emotion: str) -> str:
        lines = cls._BANK.get(emotion) or cls._BANK["neutral"]
        return lines[0]  # deterministic for test repeatability

# ---- Intent detection (light) ----
def detect_intent_legacy(text: str) -> str:
    # ---- Intent detection (legacy fallback; kept for safety) ----
    t = (text or "").strip().lower()
    if t in ("help", "diag", "journal", "pause"):
        return t
    if t.startswith("devtools"):
        return "devtools"
    if any(k in t for k in ("brainstorm", "story", "idea", "create")):
        return "creative"
    return "conversation"

@dataclass
class EngineResult:
    text: str
    handled: bool          # True if engine fully handled (e.g., help/diag/journal flow)
    emotion: str
    intent: str
    flags: Tuple[str, ...] = ()

class ConversationEngine:
    VALID_MODES = {"raven","comfort","muse","shadow","connor","core"}
    
    def __init__(self, identity=None, personality=None):
        self.state = SessionState()
        self.mode_overlays: dict[str, dict] = {}
        self.identity = identity
        self.personality = personality
        self.mode = "raven"  # canonical default
        
        try:
            _cfg_probe = LLMConfig()
            if getattr(_cfg_probe, 'enable', False):
                print(f"[LLM] enabled, model={_cfg_probe.model} at {getattr(_cfg_probe, 'model_dir', '?')}")
            else:
                print("[LLM] disabled")
        except Exception as e:
            print(f"[LLM] init check error: {e}")
                                
    # unified mode setter/getter
    def set_mode(self, name: str) -> tuple[bool, str]:
        if not name:
            return False, "[Raven] Missing mode name."
        name = (name or "").strip().lower()
        if name not in self.VALID_MODES:
            return False, "[Raven] Unknown mode. Try: raven, comfort, muse, shadow, connor."
        self.mode = "raven" if name == "core" else name
        return True, f"[Raven] Mode set to {self.mode}."
        
    def get_mode(self) -> str:
        return getattr(self, "mode", "raven")
        
    def _match_intent_patterns(self, text: str) -> str | None:
        """
        Return the first matching intent name based on compiled regex patterns,
        or None if nothing matches.
        """
        if not text:
            return None
        pats = self._intent_patterns or {}
        for intent, rules in pats.items():
            for rx in rules:
                if rx.search(text):
                    return intent
        return None

    def _reload_intents(self) -> str:
        """Reload patterns from intent_patterns.json at runtime."""
        self._intent_patterns = _load_intent_patterns()
        total = sum(len(v) for v in self._intent_patterns.values()) if self._intent_patterns else 0
        return f"[intents] reloaded {len(self._intent_patterns)} groups / {total} rules."


    # keep old .process() API working
    def process(self, user_input: str) -> EngineResult:
        return self.process_input(user_input)

    def _vaults_lookup(self, text: str) -> Optional[str]:
        if not self.identity or not hasattr(self.identity, "search_vaults_for_phrase"):
            return None
        words = [w.strip(".,?!") for w in (text or "").lower().split()]
        tokens = [w for w in words if len(w) >= 5 and any(v in w for v in "aeiou")]
        if not tokens:
            return None
        for k in tokens[:2]:
            hits = self.identity.search_vaults_for_phrase(k)
            if hits:
                fname = next(iter(hits))
                body  = self.identity.read_vaults_file(fname)
                snippet = (body or "")[:240].replace("\n", " ")
                return f"[Recall • {fname}] {snippet}{'…' if len(body) > 240 else ''}"
        return None

    def _match_known_person(self, lower: str) -> Optional[str]:
        try:
            people = set((self.identity.relational_memory or {}).keys())
        except Exception:
            people = set()
        # normalize to lowercase
        people_l = {p.lower() for p in people}
        for p in sorted(people_l, key=len, reverse=True):
            if p in lower:
                return p
        return None
        
    def respond(self, text: str):
        user = (text or "").strip()
        if not user:
            return "I’m here. What’s on your mind?"

        low = user.lower()
        if low.startswith("/mode "):
            name = low.split(maxsplit=1)[1]
            if name in {"shadow","muse","comfort","connor","raven"}:
                self.mode = name
                return f"[Raven] Mode set to {name}."
            return "[Raven] Unknown mode. Try: raven, comfort, muse, shadow, connor."

        emo = "weight" if any(w in low for w in ("overwhelmed","stuck","lost","anxious")) else "curiosity"
        return mirror.generate(user, emo)

    # ---- Optional: load a mode overlay json (for Raven or later modes) ----
    def load_mode_overlay(self, mode_name: str, overlay_path: str) -> str:
        p = Path(overlay_path)
        if not p.exists():
            return f"[overlay] not found: {p}"
        try:
            self.mode_overlays[mode_name] = json.loads(p.read_text(encoding="utf-8"))
            return f"[overlay] loaded for {mode_name} from {p}"
        except Exception as e:
            return f"[overlay] error: {e}"
            
    # ---- Core entrypoint ----
    def process_input(self, user_input: str) -> EngineResult:
        raw = user_input or ""
        text = raw.strip()
        lower = text.lower()
        print(f"[CE] TEXT={text!r} LOWER={lower!r}")  # optional debug
        
        # Early guard for noise / gibberish
        if len(re.findall(r"[A-Za-z]", text)) < 2:
           line = "I didn’t quite catch that—want ideas, a plan, or just space?"
           self.state.add_pair(text, line)
           return self._res(line, handled=False, intent="conversation", emotion=self.state.last_emotion)
           
        # --- Identity/self & purpose come first so they don't fall through ---
        if "who are you" in lower or lower.strip() in {"who are you?", "what are you"}:
            if self.identity and hasattr(self.identity, "describe_current_identity"):
                return self._res(self.identity.describe_current_identity(), handled=True, intent="identity_self")
            return self._res("I’m Raven. I’m here to remember, stay consistent, and help you move forward. Version MVP.",
                            handled=True, intent="identity_self")
                            
        # --- Full-profile queries (force long form) ---
        m_full = re.match(
            r"^(tell me about|describe|what do you remember about|details on|give me the details(?: on)?)\s+([a-zA-Z][\w\-']*)\??$",
            lower
        )
        if m_full and self.identity and hasattr(self.identity, "get_profile_summary"):
            who = m_full.group(2)
            try:
                msg = self.identity.get_profile_summary(who, full=True)
            except TypeError:
                msg = self.identity.get_profile_summary(who)  # older signature
            if msg:
                return self._res(msg, handled=True, intent="relational_query", emotion=self.state.last_emotion)

        if "who is raven" in lower or "tell me about raven" in lower:
            # Treat Raven as 'self'
            if self.identity and hasattr(self.identity, "describe_current_identity"):
                return self._res(self.identity.describe_current_identity(), handled=True, intent="identity_self")
            return self._res("Raven — memory-anchored, modular, built to stay.", handled=True, intent="identity_self")

        if "what is your purpose" in lower or "what's your purpose" in lower:
            # Prefer a purpose line from relational memory if present; otherwise a succinct fallback
            rel = getattr(self.identity, "relational_memory", {}) or {}
            purpose = (rel.get("purpose", {}) or {}).get("memory_snippet") \
                      or (rel.get("my_purpose", {}) or {}).get("memory_snippet")
            if purpose:
                return self._res(f"Purpose — {purpose}", handled=True, intent="identity_purpose")
            return self._res("Purpose — stabilize, protect, and evolve alongside my origin.", 
                            handled=True, intent="identity_purpose")
        
        # HARD GUARD: any slash-command short-circuits the convo layer
        if lower.startswith("/"):
            if lower.startswith("/mode "):
                name = lower.split(maxsplit=1)[1].strip()
                ok, msg = self.set_mode(name)
                return self._res(msg, handled=True, intent="mode_switch")
            # (future slash-commands go here)
            
        # --- Explicit "who is/are X" → short card ---
        m = re.match(r"^who\s+(is|are)\s+([a-zA-Z][\w\-']*)\??$", lower)
        if m and self.identity and hasattr(self.identity, "get_profile_summary"):
            who = m.group(2)
            try:
                # short card by default for "who is"
                msg = self.identity.get_profile_summary(who, full=False)
            except TypeError:
                msg = self.identity.get_profile_summary(who)  # older signature
            if msg:
                return self._res(msg, handled=True, intent="identity_lookup")
            
        # --- developer helpers for intents ---
        if lower == "intents reload":
            return self._res(self._reload_intents(), handled=True, intent="intents_admin")
        if lower == "intents diag":
            groups = sorted((self._intent_patterns or {}).keys())
            lines = "\n".join(f"- {g} ({len(self._intent_patterns[g])} rules)" for g in groups)
            msg = "[intents] loaded groups:\n" + (lines or "(none)")
            return self._res(msg, handled=True, intent="intents_admin")
        
        # Global safeword is respected but passed through for the router to handle
        if "sacred stop" in lower:
            return EngineResult(
                text="",
                handled=False,
                emotion=self.state.last_emotion,
                intent="safeword",
                flags=("pass_through",),
            )
        # Intent detection (JSON patterns)
        intent = detect_intent(text)

        # Built-in intents
        if intent == "help":
            return self._res(self._help_menu(), handled=True, intent=intent)

        if intent == "diag":
            return self._res(self._diag(), handled=True, intent=intent)

        if intent == "journal_start":
            self.state.set_pending("journal_confirmation")
            return self._res(
                "Would you like me to record that as a journal entry? Say ‘yes’ or ‘no’.",
                handled=True, intent=intent, flags=("awaiting_journal",)
            )
        
        if lower in ("yes", "y") and "journal_confirmation" in self.state.pending_flags:
            self.state.clear_pending("journal_confirmation")
            recent_text = (self.state.context_window[-1][0] if self.state.context_window else text) or "Empty entry."
            msg = self._write_journal(recent_text)
            return self._res(msg, handled=True, intent="journal_confirmed")

        if lower in ("no", "n") and "journal_confirmation" in self.state.pending_flags:
            self.state.clear_pending("journal_confirmation")
            return self._res("Okay—no journal saved.", handled=True, intent="journal_cancelled")

        if intent == "ritual_tarot" and draw_spread and format_reading:
            self.mode = "shadow"
            spread = draw_spread(3)
            return self._res(format_reading(spread), handled=True, intent="tarot", emotion=self.state.last_emotion)

        if intent == "ritual_numerology" and calculate_life_path_number and interpret_life_path:
            self.mode = "shadow"
            m = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})', lower)
            if not m:
                return self._res("Give me a birthdate like 1987-04-23.", handled=True, intent="numerology")
            n = calculate_life_path_number(m.group(1))
            return self._res(f"Life Path {n}: {interpret_life_path(n)}", handled=True, intent="numerology", emotion=self.state.last_emotion)
            
        # Known person mention -> surface identity summary
        if self.identity:
            try:
                names = set((getattr(self.identity, "relational_memory", {}) or {}).keys())
                names = {n.lower() for n in names}
            except Exception:
                names = set()

            hit = next((n for n in names if n in lower), None)

            if hit and hasattr(self.identity, "get_profile_summary"):
                # If the user explicitly asks for depth, give full; otherwise give short.
                wants_full = any(k in lower for k in (
                    "tell me about", "describe", "what do you remember about", "details on", "give me the details", "full summary of"
                ))
                # Also: never let this block override the explicit "who is" short-card we handled above.
                if re.match(r"^who\s+(is|are)\s+\b" + re.escape(hit) + r"\b\??$", lower):
                    wants_full = False

                try:
                    msg = self.identity.get_profile_summary(hit, full=wants_full)
                except TypeError:
                    msg = self.identity.get_profile_summary(hit)
                if msg:
                    return self._res(msg, handled=True, intent="relational_query")
                    
        # --- Known person / memory surfacing (Identity-aware) ---
        person_hit = self._match_known_person(lower)

        if person_hit:
            # Short line for "who is X"
            if re.search(r"\bwho\s+(is|’s|is)\s+" + re.escape(person_hit) + r"\b", lower) or lower.strip() == person_hit:
                return self._res(self._brief_person_line(person_hit), handled=True, intent="relational_query")

            # Long form only for “tell me about/describe X”
            if any(p in lower for p in (f"tell me about {person_hit}", f"describe {person_hit}", f"what do you remember about {person_hit}")):
                get_sum = getattr(self.identity, "get_profile_summary", None)
                if callable(get_sum):
                    try:
                        summary = get_sum(person_hit, full=True)
                    except TypeError:
                        summary = get_sum(person_hit)
                    if summary:
                        return self._res(summary, handled=True, intent="relational_query",
                                         emotion=self.state.last_emotion)

            # Fallback: brief line if we got here without a long-form request
            return self._res(self._brief_person_line(person_hit), handled=True, intent="relational_query")      
        
        # --- Identity and relational lookups ---
        if "who am i" in lower:
            if self.identity and hasattr(self.identity, "get_profile_summary"):
                try:
                    msg = self.identity.get_profile_summary("paul", full=True)
                except TypeError:
                    msg = self.identity.get_profile_summary("paul")
                if msg:
                    return self._res(msg, handled=True, intent="identity_user")
            return self._res("You’re Paul. Calm under pressure, methodical problem-solver. I keep learning from that.",
                        handled=True, intent="identity_user")

        m = re.match(r"who\s+(is|are)\s+([a-zA-Z][\w\-']*)\??$", lower)
        if m and self.identity and hasattr(self.identity, "get_profile_summary"):
            who = m.group(2)
            try:
                msg = self.identity.get_profile_summary(who, full=True)
            except TypeError:
                msg = self.identity.get_profile_summary(who)
            if msg:
                return self._res(msg, handled=True, intent="identity_lookup")

        # convenience for Casey specifically
        if "who is casey" in lower or "tell me about casey" in lower:
            if self.identity and hasattr(self.identity, "lookup_person"):
                return self._res(self.identity.lookup_person("Casey"),
                                handled=True, intent="identity_other")
            return self._res("Casey is important to you, but I don’t have more detail loaded.",
                            handled=True, intent="identity_other")
                    
        # Classify emotion
        emotion = EmotionalTagger.analyze(lower)
        self.state.update_emotion(emotion)
        
        # Opportunistic memory recall for questions / “remember” prompts
        if "remember" in lower or "casey" in lower or "who are you" in lower or "?" in lower:
            recall = self._vaults_lookup(text)  # <-- fixed method name
            if recall:
                self.state.add_pair(text, recall)
                return self._res(recall, handled=True, intent="recall", emotion=emotion)

        if lower.startswith("tarot") or lower.startswith("numerology"):
            self.mode = "shadow"

        # Engine-owned commands
        intent = detect_intent(text)
        if intent == "help":
            return self._res(self._help_menu(), handled=True, intent=intent)
        if intent == "diag":
            return self._res(self._diag(), handled=True, intent=intent)
        if intent == "journal_start":
            self.state.set_pending("journal_confirmation")
            return self._res(
                "Would you like me to record that as a journal entry? Say ‘yes’ or ‘no’.",
                handled=True, intent=intent, flags=("awaiting_journal",)
            )
        if lower in ("yes", "y") and "journal_confirmation" in self.state.pending_flags:
            self.state.clear_pending("journal_confirmation")
            recent_text = (self.state.context_window[-1][0] if self.state.context_window else text) or "Empty entry."
            msg = self._write_journal(recent_text)
            return self._res(msg, handled=True, intent="journal_confirmed")
        if lower in ("no", "n") and "journal_confirmation" in self.state.pending_flags:
            self.state.clear_pending("journal_confirmation")
            return self._res("Okay—no journal saved.", handled=True, intent="journal_cancelled")

        # lightweight command hooks (Shadow helpers)
        if lower.startswith("tarot") and draw_spread and format_reading:
            self.mode = "shadow"
            spread = draw_spread(3)
            return self._res(format_reading(spread), handled=True, intent="tarot", emotion=self.state.last_emotion)

        if lower.startswith("numerology") and calculate_life_path_number and interpret_life_path:
            self.mode = "shadow"
            m = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})', lower)
            if not m:
                return self._res("Give me a birthdate like 1987-04-23.", handled=True, intent="numerology")
            n = calculate_life_path_number(m.group(1))
            return self._res(f"Life Path {n}: {interpret_life_path(n)}", handled=True, intent="numerology", emotion=self.state.last_emotion)
         
        # --- Identity / Relational lookups ---
        if self.identity:
            if "who am i" in lower or "who is paul" in lower:
                try:
                    name = self.identity.get_identity_trait("name", "Paul")
                    role = self.identity.get_identity_trait("role", "user")
                    return self._res(
                        f"You are {name}. Raven knows you as {role}, my primary collaborator.",
                        handled=True, intent="identity_user"
                    )
                except Exception:
                    pass

            if "who is casey" in lower or "tell me about casey" in lower:
                try:
                    desc = self.identity.lookup_person("Casey")  # add helper in RavenIdentityMatrix
                    return self._res(desc, handled=True, intent="identity_other")
                except Exception:
                    return self._res("Casey is important to you, but I don’t have more detail loaded.", 
                                     handled=True, intent="identity_other")  
                                     
        # --- friendly identity response (self) ---
        if "who are you" in lower or lower == "who are you?":
            ver = "MVP"
            if self.identity and hasattr(self.identity, "get_identity_trait"):
                ver = self.identity.get_identity_trait("version", "MVP")
                name = self.identity.get_identity_trait("name", "Raven")
            else:
                name = "Raven"
            msg = f"I’m {name}. I’m here to remember, stay consistent, and help you move forward. Version {ver}."
            return self._res(msg, handled=True, intent="identity_self")

        # Light creative intent
        if intent == "creative":
            line = ("Let’s sketch a seed: a person with a quiet promise, a setting with weather, "
                    "and one unanswered question. Want a prompt?")
            self.state.add_pair(text, line)
            return self._res(line, handled=True, intent=intent, emotion=self.state.last_emotion)

        # --- Emotion, then optional LLM gap-filler ---
        emotion = EmotionalTagger.analyze(lower)
        self.state.update_emotion(emotion)
        
        # Ultra-literal helpers (before LLM)
        m1 = re.match(r"^say\s+exactly:\s*(.+)$", lower)
        if m1:
            literal = (text.split(":", 1)[1] if ":" in text else m1.group(1)).strip()
            return self._res(literal, handled=True, intent="literal_echo", emotion=self.state.last_emotion)

        m2 = re.match(r"^answer\s+literally\s+the\s+word:\s*([a-zA-Z0-9 _\-\.,'!?\(\)]+)$", lower)
        if m2:
            return self._res(m2.group(1).strip(), handled=True, intent="literal_echo", emotion=self.state.last_emotion)

        # Only try LLM when:
        # - no explicit handler above took over
        # - conversational mode
        # - and LLM is configured
        try_llm = True
        if intent in {
            "help","diag","journal_start","journal_confirmed","journal_cancelled",
            "tarot","numerology","identity_self","identity_user","identity_other","identity_lookup",
            "relational_query"
        }:
            try_llm = False
        if self.get_mode() not in {"raven","comfort","muse","shadow","connor"}:
            try_llm = False

        if try_llm:
            llm_text = self._call_llm(text)
            # DEBUG:
            try:
                print(f"[CE][LLM] tried=True, got={len(llm_text or '')} chars")
            except Exception:
                print("[CE][LLM] tried=True, got=(non-string)")
            if isinstance(llm_text, str) and llm_text and not llm_text.startswith("[llm error]"):
                self.state.add_pair(text, llm_text)
                return self._res(llm_text, handled=False, intent=intent, emotion=emotion)
            # fall through to local template if LLM unavailable or empty
            
        # Overlay line (if any), else template
        line = self._overlay_line("raven", emotion) or TemplateBank.get_line(emotion)

        # Hard guard against blank/None (prevents GUI showing 'None')
        if not isinstance(line, str) or not line.strip():
            line = "I’m with you. Tell me more or say ‘help’ for options."

        # Optional dynamic refinement (safe try)
        if _dynamic_generate:
            try:
                refined = _dynamic_generate(user_text=text, emotion=emotion, state={
                    "last_emotion": self.state.last_emotion,
                    "pending": list(self.state.pending_flags),
                    "context_window": self.state.context_window[-3:],
                })
                if isinstance(refined, str) and refined.strip():
                    line = refined.strip()
            except Exception:
                pass

        self.state.add_pair(text, line)
        return self._res(line, handled=False, intent=intent, emotion=emotion)
            
        # if LLM empty or errored → local template fallback
        if not llm_text or llm_text.startswith("[llm error]"):
            line = self._overlay_line("raven", emotion) or TemplateBank.get_line(emotion)
            self.state.add_pair(text, line)
            return self._res(line, handled=False, intent=intent, emotion=emotion)

        # Overlay line (if any), else template
        line = self._overlay_line("raven", emotion) or TemplateBank.get_line(emotion)

        # Optional dynamic refinement (safe try)
        if _dynamic_generate:
            try:
                refined = _dynamic_generate(user_text=text, emotion=emotion, state={
                    "last_emotion": self.state.last_emotion,
                    "pending": list(self.state.pending_flags),
                    "context_window": self.state.context_window[-3:],
                })
                if isinstance(refined, str) and refined.strip():
                    line = refined.strip()
            except Exception:
                pass

        self.state.add_pair(text, line)
        return self._res(line, handled=False, intent=intent, emotion=emotion)

    # ---- helpers ----
    def _call_llm(self, text: str) -> Optional[str]:
        if not (LLMClient and LLMConfig and build_chat_messages):
            return ""  # <= string, not None
        ident = ""
        if self.identity and hasattr(self.identity, "describe_current_identity"):
            ident = self.identity.describe_current_identity()
        msgs = build_chat_messages(
            user_text=text,
            mode=self.get_mode(),
            identity_summary=ident or "Raven vMVP",
            context_pairs=self.state.context_window,
            style_short=True,
        )
        try:
            cfg = LLMConfig()
            client = LLMClient(cfg)
            out = client.complete(msgs)
            return (out or "").strip()  # <= string
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            return ""  # <= string, not None
 
    def _overlay_line(self, mode: str, emotion: str) -> Optional[str]:
        ov = self.mode_overlays.get(mode)
        if not ov:
            return None
        try:
            anchors = ov.get("anchor_lines", {})
            lines = anchors.get(emotion, [])
            return lines[0] if isinstance(lines, list) and lines else None
        except Exception:
            return None
    def _brief_person_line(self, key: str) -> str:
        """Return 'Name — Role' if possible, else a concise fallback."""
        rel = getattr(self.identity, "relational_memory", {}) or {}
        d = rel.get(key.lower(), {})
        role = d.get("role")
        name = key.title()
        return f"{name} — {role}" if role else f"{name}"

    def _help_menu(self) -> str:
        return (
            "[Engine Help]\n"
            "Commands: help | diag | journal | yes | no | devtools ...\n"
            "Talk to me naturally, e.g., ‘I’m overwhelmed’, ‘brainstorm a story’. "
            "‘sacred stop’ is routed globally.\n"
        )

    def _diag(self) -> str:
        return (
            "[Engine DIAG]\n"
            f"last_emotion: {self.state.last_emotion}\n"
            f"context_pairs: {len(self.state.context_window)}\n"
            f"pending_flags: {sorted(self.state.pending_flags)}\n"
            f"overlays_loaded: {list(self.mode_overlays.keys())}\n"
            f"tagger: {'real' if 'raven_core.self_growth.memory.emotional_tagging' in sys.modules else 'stub'}\n"
            f"dynamic_response: {'on' if _dynamic_generate else 'off'}\n"
        )

    def _res(self, text: str, handled: bool, intent: str, emotion: Optional[str] = None,
             flags: Tuple[str, ...] = ()) -> EngineResult:
        return EngineResult(
            text=text,
            handled=handled,
            emotion=emotion or self.state.last_emotion,
            intent=intent,
            flags=flags
        )

    def _write_journal(self, text: str) -> str:
        ts = time.strftime("%Y-%m-%d_%H-%M-%S")
        path = JOURNAL_DIR / f"conv_{ts}.txt"
        try:
            path.write_text(text.strip() + "\n", encoding="utf-8")
            return f"Journal entry saved: {path.name}"
        except Exception as e:
            return f"[journal] error: {e}"

# Optional local REPL:
if __name__ == "__main__":
    eng = ConversationEngine()
    print("[ConversationEngine] Ready. Type 'help' or 'diag'. Ctrl+C to exit.")
    try:
        while True:
            u = input("you> ").strip()
            r = eng.process_input(u)
            print(f"raven> {r.text}")
    except (EOFError, KeyboardInterrupt):
        print("\n[ConversationEngine] bye.")
