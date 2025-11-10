# comfort_mode.py
import os, sys, json, random, importlib.util
from pathlib import Path

# Prefer RAVEN_ROOT → fall back to walking up to repository root
# .../container/aeris_core/app/modes/comfort/comfort_mode.py -> parents[6] == repo root
raven_root = Path(os.environ.get("RAVEN_ROOT", Path(__file__).resolve().parents[6]))
app_path   = raven_root / "container" / "aeris_core" / "app"

for p in (
    app_path,
    app_path / "tools",
    app_path / "tools" / "sandbox",
    app_path / "tools" / "sandbox" / "parsing",
    raven_root / "raven_core" / "self_growth" / "memory",  # for memory.* imports
):
    p = str(p)
    if p not in sys.path:
        sys.path.insert(0, p)

# --- Overlay Loader ---
def load_comfort_overlay():
    overlay_path = app_path / 'modes' / 'comfort' / 'comfort_personality_overlay.json'
    try:
        with open(overlay_path, 'r', encoding='utf-8') as f:
            overlay_data = json.load(f)
        print(f"[Overlay] Comfort Mode personality overlay loaded with tags: {overlay_data.get('overlay_tags', [])}")
        return overlay_data
    except FileNotFoundError:
        print("[Warning] Comfort personality overlay not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"[Error] Failed to decode overlay: {e}")
        return {}

# Core imports with fallback protection
try:
    from utilities.rituals import breath_sequence
    from modes.comfort import comfort_templates
    from utilities.mirroring import reflective_response
    from utilities.symbolics import comfort_symbols
    from utilities.audio.tone_to_tts import get_tts_settings
    from memory.session_emotion import emotion_tracker
    from modes.comfort import comfort_support
    from utilities.herbal_lookup import query_remedy
except ImportError as e:
    print(f"[ComfortMode] Import issue: {e}")

class ComfortMode:
    def __init__(self, identity_core=None, user_profile=None, memory_vault=None):
        self.identity_core = identity_core
        self.user_profile = user_profile
        self.memory_vault = memory_vault
        self.presence_active = False
        self.overlay = load_comfort_overlay()  # Overlay loaded here

        if self.identity_core:
            self.name = self.identity_core.get_identity_trait("name") or "Raven"
            self.version = self.identity_core.get_identity_trait("version") or "undefined"
        else:
            self.name = "Raven"
            self.version = "undefined"

    def respond_to(self, user_input):
        intro = (
            f"I'm {self.name}, still piecing some things together."
            if self.identity_core and getattr(self.identity_core, 'fallback_mode', False)
            else f"{self.name}, version {self.version}"
        )

        if not user_input.strip():
            return f"{intro}. You said nothing—try again?"

        user_input_lc = user_input.lower()

        # Entrypoint detection (from overlay)
        entrypoints = self.overlay.get("entrypoints", [])
        if any(ep in user_input_lc for ep in entrypoints):
            return random.choice(self.overlay.get("anchor_phrases", ["I'm here."]))

        if "how are you" in user_input_lc:
            return f"{intro}. I'm here. Listening. What's on your mind?"
        elif "hello" in user_input_lc or "hi" in user_input_lc:
            return f"{intro}. Always good to hear from you."
        elif "paul" in user_input_lc:
            return f"{intro}. You’re here. That helps."

        return self.process_input(user_input)

    def activate(self):
        self.presence_active = True
        try:
            return comfort_templates.initial_greeting()
        except Exception as e:
            return f"[ComfortMode] Activated – greeting unavailable: {e}"

    def process_input(self, user_input):
        print("[ComfortMode] process_input activated.")
        lowered = user_input.lower()

        if "safeword" in lowered:
            return "Comfort pause initiated. You're safe."

        if any(x in lowered for x in ["herb", "tea", "remedy", "scent", "aroma", "natural"]):
            try:
                result = query_remedy(user_input)
                return f"[HerbalSupport] {result}"
            except Exception as e:
                return f"[ComfortMode] Herbal query failed: {e}"

        # Example: fallback to overlay if lost or out-of-bounds
        if self.overlay.get("fallback_responses"):
            fallback = random.choice(self.overlay["fallback_responses"])
        else:
            fallback = "[ComfortMode] She’s still here. Calm, grounded, and nearby if you need her."

        try:
            # Load personality core dynamically
            personality_path = app_path / 'voice_core' / 'raven_personality_core.py'
            spec = importlib.util.spec_from_file_location("raven_personality_core", str(personality_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            personality_instance = module.RavenPersonalityCore(self.identity_core)
            response = personality_instance.process_input(user_input)
            return response or fallback
        except Exception as e:
            print(f"[ComfortMode] Core fallback triggered: {e}")
            if self.identity_core:
                return f"{self.identity_core.describe_current_identity()} I’m grounded here with you."
            return fallback

    def deactivate(self):
        self.presence_active = False
        try:
            return comfort_templates.exit_sequence()
        except Exception:
            return "[ComfortMode] Exiting comfort mode. She’s still close."
