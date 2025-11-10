# reflective_context_manager.py 

import json
from datetime import datetime
from pathlib import Path

from raven_path_initializer import set_project_root
set_project_root()

from utilities.path_refactor import get_full_path

# --- ethos load ---
def _load_raven_ethos() -> str:
    try:
        return Path(get_full_path("vaults/raven_training_data.txt")).read_text(encoding="utf-8")
    except Exception as e:
        print(f"[ReflectiveManager] Failed to load ethos data: {e}")
        return ""

_raven_ethos_data = _load_raven_ethos()

# --- tiny shims used by personality core ---
def get_recent_tone() -> str:  # keep signature simple
    return "neutral"

def get_context_tags():
    return []

# --- helper used both top-level and instance method ---
def enrich_reflection(text: str) -> str:
    if not _raven_ethos_data:
        return text
    tl = (text or "").lower()
    ref = _raven_ethos_data.lower()
    if "i'm not sure" in tl and "growth" in ref:
        return text + " But maybe that’s part of how I grow."
    if "hard to explain" in tl and "pattern" in ref:
        return text + " Still, there’s probably a pattern forming."
    return text

class ReflectiveContextManager:
    def __init__(self):
        self.reflections_dir = Path(get_full_path("self_growth/journals/reflection/reflections"))
        self.context_log_path = Path(get_full_path("self_growth/journals/reflection/context_history.json"))

    # read most recent reflection files (if any)
    def load_reflections(self):
        out = []
        if self.reflections_dir.exists():
            for fp in sorted(self.reflections_dir.glob("*.txt"), key=lambda p: p.name, reverse=True):
                try:
                    s = fp.read_text(encoding="utf-8").strip()
                    if s:
                        out.append({"filename": fp.name, "content": s})
                except Exception as e:
                    print(f"[ReflectiveManager] Error reading {fp.name}: {e}")
        return out

    # instance wrapper (reuses top-level helper for consistency)
    def enrich_reflection(self, text: str) -> str:
        return enrich_reflection(text)

    def get_context_snippets(self, max_snippets=5):
        refs = self.load_reflections()
        if not refs:
            return ["No reflections available."]
        return [self.enrich_reflection(r["content"][:280]) for r in refs[:max_snippets]]

    def save_context_event(self, event):
        self.context_log_path.parent.mkdir(parents=True, exist_ok=True)
        history = []
        if self.context_log_path.exists():
            try:
                history = json.loads(self.context_log_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                history = []
        history.append({"timestamp": datetime.now().isoformat(), "event": event})
        self.context_log_path.write_text(json.dumps(history, indent=4), encoding="utf-8")

    def get_recent_context(self, limit=3):
        if not self.context_log_path.exists():
            return []
        try:
            return json.loads(self.context_log_path.read_text(encoding="utf-8"))[-limit:]
        except json.JSONDecodeError:
            return []

    def reflect_and_summarize(self):
        return "Reflection Summary:\n" + "\n---\n".join(self.get_context_snippets())
