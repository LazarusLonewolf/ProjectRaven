# raven_core_controller.py  (clean minimal controller)

from __future__ import annotations
import sys, importlib.util
from pathlib import Path
from typing import Optional

from raven_path_initializer import set_project_root, initialize_paths
set_project_root(); initialize_paths()

CORE_DIR = Path(__file__).resolve().parent
APP_DIR  = CORE_DIR.parent

# Ensure imports work
for p in (
    str(CORE_DIR),
    str(CORE_DIR / "self_growth" / "analysis"),
    str(CORE_DIR / "self_growth" / "journals"),
    str(CORE_DIR / "self_growth" / "memory"),
    str(APP_DIR),
):
    if p not in sys.path:
        sys.path.append(p)

from raven_identity_matrix import RavenIdentityMatrix as IdentityMatrix
from reflective_context_manager import ReflectiveContextManager
from raven_core.conversation_engine import ConversationEngine

try:
    from raven_personality_core import RavenPersonalityCore as PersonalityCore
except Exception:
    spec = importlib.util.spec_from_file_location("raven_personality_core", str(APP_DIR / "raven_personality_core.py"))
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    PersonalityCore = mod.RavenPersonalityCore

class RavenCoreController:
    def __init__(self):
        self.name = "Raven"; self.version = "0.9.1"; self.origin = "Casey's design."
        self.identity = IdentityMatrix()
        self.context_manager = ReflectiveContextManager()
        self.personality = PersonalityCore(identity_matrix=self.identity)
        self.engine = ConversationEngine(identity=self.identity, personality=self.personality)

    def describe_current_identity(self) -> str:
        return f"I am {self.name}, version {self.version}. I exist to evolve, stabilize, and remember."

    def respond_to(self, user_text: Optional[str]) -> str:
        try:
            text = (user_text or "").strip()
            if not text:
                return "I’m here and listening."
            res = self.engine.process_input(text)
            out = getattr(res, "text", "") or ""
            return out.strip() or "I’m here and listening."
        except Exception:
            return "I’m here and listening."

# Bus helpers
_core_singleton: Optional[RavenCoreController] = None

def _get_core() -> RavenCoreController:
    global _core_singleton
    if _core_singleton is None:
        _core_singleton = RavenCoreController()
    return _core_singleton

def send_to_raven_core(message: Optional[str]) -> str:
    return _get_core().respond_to(message)

if __name__ == "__main__":
    _get_core()
