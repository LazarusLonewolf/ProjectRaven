# raven_core/intent_loader.py
from __future__ import annotations
import json, re
from pathlib import Path

# Resolve to .../raven_core/intent_patterns.json (same folder as THIS file)
_CONFIG_PATH = Path(__file__).resolve().parent / "intent_patterns.json"

# Compile cache
_compiled: dict[str, list[re.Pattern]] | None = None

def load_intent_patterns() -> dict[str, list[re.Pattern]]:
    """Loads and compiles regex intent patterns (case-insensitive)."""
    global _compiled
    try:
        text = _CONFIG_PATH.read_text(encoding="utf-8")
        raw = json.loads(text)
        compiled: dict[str, list[re.Pattern]] = {}
        for intent, patterns in (raw or {}).items():
            group: list[re.Pattern] = []
            for p in patterns or []:
                try:
                    group.append(re.compile(p, re.IGNORECASE))
                except re.error as e:
                    print(f"[intent_loader] bad pattern for '{intent}': {p} ({e})")
            compiled[intent] = group
        _compiled = compiled
    except Exception as e:
        print(f"[intent_loader] load error: {e}")
        _compiled = {}
    return _compiled

def get_intent_patterns() -> dict[str, list[re.Pattern]]:
    """Accessor that lazy-loads once."""
    global _compiled
    if _compiled is None:
        return load_intent_patterns()
    return _compiled

def detect_intent(text: str, default: str = "conversation") -> str:
    """
    Priority scan across command-like intents, then any match.
    """
    t = (text or "").strip()
    pats = get_intent_patterns()

    priority = [
        "mode_switch", "diag", "help",
        "journal_start", "journal_confirm", "journal_cancel",
        "ritual_tarot", "ritual_numerology",
        "identity", "smalltalk", "creative",
    ]

    def _match_in(keys):
        for k in keys:
            for rgx in pats.get(k, []):
                if rgx.search(t):
                    return k
        return None

    hit = _match_in(priority)
    if hit:
        return hit

    for k, group in pats.items():
        for rgx in group:
            if rgx.search(t):
                return k

    return default
