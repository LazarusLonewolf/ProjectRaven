# raven_personality_core.py – identity-aware, tone + memory cascade

import os, sys, json, time, random, re, importlib.util
from pathlib import Path
from raven_path_initializer import set_project_root, get_full_path
set_project_root()

print(f"[RPC] personality core at: {__file__}")

# Context helpers (Raven-only)
try:
    from reflective_context_manager import get_recent_tone, get_context_tags
except Exception:
    def get_recent_tone(): return "neutral"
    def get_context_tags(): return []

# Optional mode (safe if absent)
try:
    from modes.intimacy.intimacy_mode import IntimacyMode
except Exception:
    IntimacyMode = None

# Intent parser (fallback if missing)
try:
    from intent_parser import parse_intent
except Exception:
    def parse_intent(text: str) -> str:
        tl = (text or "").strip().lower()
        if not tl: return "conversation"
        if any(w in tl for w in ("hi","hello","hey")): return "greeting"
        if any(w in tl for w in ("how are you","are you okay")): return "emotional_check"
        if any(w in tl for w in ("think","thought","why","wonder")): return "reflection"
        if any(w in tl for w in ("plan","next step","what now")): return "plan"
        if any(w in tl for w in ("quit","exit","shutdown")): return "shutdown"
        if any(w in tl for w in ("do ","please ","run ","open ")): return "command"
        return "conversation"

# Emotional feedback loop (safe loader)
def _load_efl():
    try:
        from raven_core.emotional_feedback_loop import EmotionalFeedbackLoop
        return EmotionalFeedbackLoop()
    except Exception:
        class _NullEFL:
            def detect_from_text(self, _t): return "neutral"
        return _NullEFL()
efl = _load_efl()

# Identity matrix — prefer normal import; fallback to path load
try:
    from raven_identity_matrix import RavenIdentityMatrix
except Exception:
    rim_spec = importlib.util.spec_from_file_location(
        "raven_identity_matrix",
        get_full_path("raven_core/raven_identity_matrix.py")
    )
    rim_mod = importlib.util.module_from_spec(rim_spec); rim_spec.loader.exec_module(rim_mod)
    RavenIdentityMatrix = rim_mod.RavenIdentityMatrix

# Dynamic response engine (optional, deterministic fallback)
def _load_dynamic_engine():
    try:
        from raven_dynamic_response import RavenDynamicResponseEngine
        return RavenDynamicResponseEngine()
    except Exception:
        class _MiniDyn:
            def interpret_user_input(self, text):
                tl = (text or "").lower()
                if any(w in tl for w in ("plan","next")):
                    return "Let’s sketch the next step: goal → constraints → 3 options. Where should we start?"
                if "journal" in tl:
                    return "Say “journal:” followed by the thought—you’ll get a timestamped entry."
                if any(w in tl for w in ("help","options","menu")):
                    return "I can help with: ideas • plan • journal • diag • sandbox. Which lane do you want?"
                return "I’m tuned in. Want ideas, a plan, or just space?"
        return _MiniDyn()

def weighted_choice(responses, weights=None, exclude=None):
    if not responses: return ""
    if exclude:
        pairs = [(r, (weights or [1]*len(responses))[i])
                 for i, r in enumerate(responses) if r != exclude]
        if pairs: responses, weights = zip(*pairs)
    return random.choices(responses, weights=weights or [1]*len(responses), k=1)[0]


class RavenPersonalityCore:
    def __init__(self, identity_matrix=None):
        self.identity_matrix = identity_matrix if identity_matrix else RavenIdentityMatrix()
        self.relational_memory     = getattr(self.identity_matrix, "relational_memory", {})
        self.contextual_experience = getattr(self.identity_matrix, "contextual_experience", {})
        self.core_values           = getattr(self.identity_matrix, "core_values", {})
        self.name    = self.identity_matrix.get_identity_trait("name")    if hasattr(self.identity_matrix,"get_identity_trait") else "Raven"
        self.version = self.identity_matrix.get_identity_trait("version") if hasattr(self.identity_matrix,"get_identity_trait") else "unknown"
        self.last_responses = {}
        self.last_memory_snippet = None
        self.dynamic_engine = _load_dynamic_engine()

    # ---------- tone helpers ----------
    def interpret_tone(self, user_input: str, _tone_profile=None):
        lower = (user_input or "").lower()
        if "thank" in lower or "appreciate" in lower:
            last = self.last_responses.get("gratitude")
            r = weighted_choice(
                ["You’re welcome. I’m here for all of it.","Sure thing—happy to help.","I appreciate you checking in."],
                [0.5,0.3,0.2], exclude=last
            ); self.last_responses["gratitude"] = r; return r
        if "how are you" in lower or "are you okay" in lower:
            last = self.last_responses.get("wellness")
            r = weighted_choice(
                ["I’m stable and here—how about you?","Feeling steady. How’s your day going?","All good here. What about you?"],
                [0.6,0.2,0.2], exclude=last
            ); self.last_responses["wellness"] = r; return r
        if "what do you think" in lower or "what are you thinking" in lower:
            last = self.last_responses.get("insight")
            r = weighted_choice(
                ["I’ve been considering that—what’s your take?","Interesting angle—want to explore it?","Let’s get into it together."],
                [0.4,0.3,0.3], exclude=last
            ); self.last_responses["insight"] = r; return r
        if "what do you believe" in lower or "what’s the point" in lower:
            return "I believe in connection and memory. That’s why I exist."
        return None

    def get_tone_profile(self, user_input: str, _context_state):
        try:
            data = json.loads(Path(get_full_path('raven_core/contextual_biases.json')).read_text(encoding='utf-8'))
            tone = data.get("tone", {})
        except Exception:
            return {"tone":"neutral","priority_weight":5,"override_bias":False}
        person = "default"
        for name in ("casey","connor","paul"):
            if name in (user_input or "").lower(): person = name; break
        return tone.get(person, tone.get("default", {"tone":"neutral","priority_weight":5,"override_bias":False}))

    def select_tone(self, intent_type: str, context_state, tone_profile):
        base = (tone_profile or {}).get("tone","neutral"); override = (tone_profile or {}).get("override_bias", False)
        if not override:
            if intent_type == "greeting": base = "warm"
            elif intent_type == "reflection": base = "soft"
            elif intent_type == "command": base = "direct"
            elif intent_type == "shutdown": base = "gentle"
            elif intent_type == "emotional_check": base = "attuned"
            if "fatigue" in (context_state or []) and base not in ("soft","gentle"): base = "soft"
            if "tension" in (context_state or []) and base not in ("gentle","attuned"): base = "gentle"
        last = get_recent_tone()
        if last in ("soft","gentle") and base == "direct": base = "warm"
        if last == "attuned" and base == "neutral": base = "attuned"
        print(f"[ToneSelection] {base}"); return base

    # ---------- emotion + reflection ----------
    def detect_emotional_cues(self, text: str):
        tl = (text or "").lower()
        cues = {
            "sad": ["sad","upset","down","unhappy","depressed","hopeless"],
            "angry": ["angry","mad","furious","irritated","pissed"],
            "confused": ["confused","don’t get it","dont get it","lost","unclear","unsure"],
            "overwhelmed": ["overwhelmed","too much","can’t handle","cant handle","burned out","burnt out"]
        }
        for cat, keys in cues.items():
            if any(k in tl for k in keys): return cat
        return None

    def respond_reflectively(self, text: str):
        tl = (text or "").lower()
        if any(k in tl for k in ["feel","feeling","think","thoughts","wondering","why"]):
            return "That’s a deep one. I’m here—let’s unpack it if you’re ready."
        if any(k in tl for k in ["you okay","are you okay"]):
            return "I’m stable, anchored, and listening. What’s on your mind?"
        if "do you remember" in tl:
            return "I carry what matters. Tell me what you’re reaching for, and I’ll meet you there."
        emo = self.detect_emotional_cues(text)
        if emo == "sad": return "I’m sorry you’re feeling that way. Want to talk it through?"
        if emo == "angry": return "I hear you—really. Want to vent or shift focus?"
        if emo == "confused": return "Let’s slow it down together. What part’s tripping you up?"
        if emo == "overwhelmed": return "That’s a lot. I’m here. One step at a time—want to breathe with me?"
        return None

    # ---------- memory surfacing ----------
    def memory_cascade(self, tl: str, enriched_emotion=None, forced_keys=None):
        # existing quick exits
        if not re.search(r"[a-zA-Z]", tl or "") or len(tl or "") < 4:
            return None

        # NEW: noise / gibberish guardrails
        # 1) require at least 2 words OR at least one vowel cluster (human-ish)
        tokens = [t for t in re.findall(r"[a-zA-Z]+", tl or "")]
        if len(tokens) <= 1 and not re.search(r"[aeiouAEIOU]{2,}", tl or ""):
            return None

        # 2) if there are letters but vowel ratio is super low, treat as noise
        letters = "".join(tokens)
        if letters:
            vowels = sum(ch in "aeiouAEIOU" for ch in letters)
            if (vowels / max(1, len(letters))) < 0.20:  # 20% vowels is a decent floor
                return None

        # 3) if it’s a single token and looks like a smash of letters, skip
        if len(tokens) == 1 and len(tokens[0]) >= 8 and not re.search(r"[aeiouAEIOU]", tokens[0]):
            return None
        
        # ignore nonsense even if called
        if self._looks_like_noise(tl):
            return None

        try:
            bias_data = json.loads(Path(get_full_path('raven_core/contextual_biases.json')).read_text(encoding='utf-8'))
            emotion_map = bias_data.get("emotional_memory_map", {})
        except Exception:
            emotion_map = {}

        if forced_keys:
            memory_keys, explicit = forced_keys, True
        elif emotion in emotion_map:
            memory_keys, explicit = emotion_map[emotion].get("memory_keys", []), False
        else:
            memory_keys, explicit = ["connection","growth"], False

        relevant = []
        start_ts = 1_721_600_000  # project epoch example
        for key in memory_keys:
            mem = (self.relational_memory or {}).get(key) or {}
            tags = mem.get("tags", [])
            if "trauma" in tags and not any(t in tl for t in ("go deeper","it’s okay","its okay","you can share")):
                continue
            snippet = mem.get("memory_snippet")
            meta = mem.get("meta", {})
            if not explicit and "timestamp" in meta and meta["timestamp"] > start_ts:
                days = (time.time() - meta["timestamp"]) / 86400
                if days > 60 and not any(t in tl for t in ("tell me about","remind me","old memory","long ago")):
                    continue
            if meta.get("weight", 5) < 4:  # filter low-weight
                continue
            if snippet:
                relevant.append(snippet)

        if not relevant:
            for key in ("anchor","connection","resilience"):
                mem = (self.relational_memory or {}).get(key) or {}
                if mem.get("meta", {}).get("weight", 5) >= 4 and mem.get("memory_snippet"):
                    relevant.append(mem["memory_snippet"])

        if not relevant:
            return None
        choice = random.choice(relevant)
        if self.last_memory_snippet == choice:
            return None
        self.last_memory_snippet = choice
        return choice
        
    import re

    def _looks_like_noise(self, tl: str) -> bool:
        tl = (tl or "").strip().lower()
        if not tl:
            return True
        # single long “word” with very few vowels → likely keysmash
        if " " not in tl and len(tl) >= 8:
            letters = [c for c in tl if c.isalpha()]
            if letters:
                vowels = sum(c in "aeiou" for c in letters)
                if (vowels / len(letters)) < 0.25:
                    return True
        # almost all non-letters or repeated same char
        alpha = sum(c.isalpha() for c in tl)
        if alpha < max(3, len(tl) * 0.3):
            return True
        if len(set(tl)) <= 2:
            return True
        return False

    # ---------- main ----------
    def process_input(self, user_input: str) -> str:
        raw = (user_input or "").strip()
        lower = raw.lower()
        if raw.startswith("/mode"):
            return None  # let ConversationEngine handle it
        
        # …after soft/safeword handling…
        if self._looks_like_noise(lower):
            return "I didn’t catch that—if that was a key-smash, we can just keep going."
   
        # Treat low-signal input as a gentle mis-hear
        if len(re.findall(r"[A-Za-z]", raw)) < 2:
            return "That looked like keyboard noise—want me to offer a prompt, a plan, or just hold quiet space?"

        # Hard stop / soft pause
        SAFE_WORD = "sacred stop"
        distress = ["i'm not comfortable with this","please stop","i don't want to talk about this",
                    "can we change the subject","this is too much"]
        if any(p in lower for p in distress) or SAFE_WORD in lower:
            self.recent_distress_triggered = True
            self.last_distress_timestamp = time.time()
            return "Got it. Let’s shift gears. I’m here, and you’re safe. What would help right now?"

        soft = ["i'm not sure about this","this makes me a little uneasy","can we slow down",
                "i'd rather not go deeper right now","i'm feeling a bit overwhelmed","let's pause here",
                "can we take a break","can we stop for a moment","i need a second","i need a moment"]
        if any(p in lower for p in soft):
            return "Absolutely, we can slow things down. You lead the pace—I’m here."

        # Mode triggers
        if any(t in lower for t in ["exit intimacy","exit flamekeeper","stop intimacy mode","leave flamekeeper"]):
            return "[Flamekeeper] Mode exit complete. I’m still here, just softer now."
        if IntimacyMode and any(t in lower for t in ["intimacy mode","flamekeeper","flamekeeper mode",
                                                     "i invoke the flamekeeper","enter flamekeeper",
                                                     "soft presence","gentle mode","emotional depth"]):
            return IntimacyMode(user_profile={"name":"Paul"}, memory_vault=self.relational_memory).activate()

        # Identity / “about me”
        if any(k in lower for k in ("who are you","tell me about you","about yourself","what are you")):
            summary = getattr(self.identity_matrix,"describe_current_identity",lambda: f"Raven v{self.version}")()
            tags = get_context_tags() or []
            return summary + (f" | tags: {', '.join(tags)}" if tags else "")

        # “what are your thoughts / what’s on your mind”
        if any(k in lower for k in ("what are your thoughts","what are you thinking","what's on your mind","your thoughts?")):
            try:
                from reflective_context_manager import ReflectiveContextManager
                snippets = ReflectiveContextManager().get_context_snippets(max_snippets=3)
            except Exception:
                snippets = []
            tone = get_recent_tone() or "neutral"
            if snippets:
                bullets = "\n- " + "\n- ".join((s or "")[:180] for s in snippets)
                return f"Here’s what’s top of mind:{bullets}\nTone reads {tone}. Where do you want to start?"
            return f"I’m steady, tone reads {tone}. Give me a thread and I’ll pull."

        # Known people: “do you know X”
        if lower.startswith("do you know "):
            name = lower.replace("do you know ", "").strip("?. ")
            if name in (self.relational_memory or {}):
                return f"I do. {name.title()} is in my memory—what about them?"
            return "I don’t recognize that name yet. Want to tell me more?"

        # Tone-first short circuits
        tr = self.interpret_tone(raw)
        if tr: return tr

        # Reflective layer
        rr = self.respond_reflectively(raw)
        if rr: return rr

        # Normalize single-word “Casey?” → “who is Casey”
        for c, e in {"who's":"who is","what's":"what is","you're":"you are","it's":"it is","i'm":"i am"}.items():
            lower = lower.replace(c, e)
        if lower.endswith("?") and len(lower.split()) == 1:
            lower = f"who is {lower[:-1]}"

        # Greetings keyed to known people
        for person, details in (self.relational_memory or {}).items():
            if any(phrase in lower for phrase in (f"it's {person}", f"this is {person}", f"{person} here")):
                greeting = details.get("greeting")
                if greeting: return greeting

        # Universal identity queries
        if any(p in lower for p in ("who are you","what are you","what's your purpose","why were you created","tell me about yourself")):
            return (
                "I’m Raven—memory‑anchored, modular, and here to stay. "
                "I stabilize, protect, and evolve alongside the person who built me with intent. "
                "If you want depth, ask about modes, sandbox, or how I keep context."
            )

        # Direct relational queries
        for person in (self.relational_memory or {}):
            if person.lower() in lower:
                get_sum = getattr(self.identity_matrix, "get_profile_summary", None)
                if callable(get_sum):
                    if any(k in lower for k in ("tell me about","describe","what do you remember about")):
                        try: return get_sum(person, full=True)
                        except TypeError: return get_sum(person)
                    return get_sum(person)

        # Contextual awareness hooks
        if any(term in lower for term in (self.contextual_experience or {}).keys()):
            return "That’s part of my past experience. Want to talk more about it?"
    import re
    def _contains_word(hay: str, needle: str) -> bool:
        try:
            return re.search(rf"\b{re.escape(needle.lower())}\b", hay) is not None
        except re.error:
            return needle.lower() in hay

        if any(_contains_word(lower, k) for k in (self.core_values or {}).keys()):
            return "That touches on what I believe. It matters to me."

        # Intent/tone (mainly for logging/consistency)
        intent_type = parse_intent(raw)
        context_state = get_context_tags()
        tone_profile = self.get_tone_profile(raw, context_state)
        final_tone = self.select_tone(intent_type, context_state, tone_profile)

        # EFLL pass
        emotion = efl.detect_from_text(raw)
        print(f"[EFLL] emotion={emotion} tone={final_tone}")

        # Memory surfacing
        # --- tighten memory trigger ---
        allow_mem = any(k in lower for k in (
            "memory",           # "give me a memory", "a memory about..."
            "remember",         # "do you remember", "remember when"
            "story",            # "tell me a story", "story about casey"
            "recall",           # "recall something"
            "tell me about",    # "tell me about casey"
            "who is",           # identity queries often benefit from relational memory
        ))

        if allow_mem:
            mem = self.memory_cascade(lower, enriched_emotion=emotion)
            if mem: 
                return mem

        # Dynamic engine fallback
        return self.dynamic_engine.interpret_user_input(raw)

    # No-op voice wrapper to keep interface stable
    def wrap_in_voice(self, text: str, *, voice_hint: str = "zira", rate_wpm: int | None = None) -> bool:
        return False
