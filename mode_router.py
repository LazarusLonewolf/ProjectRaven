# mode_router.py — minimal, stable mode loader

import os
import sys
import importlib
from pathlib import Path

# Core controller (identity_core is used by modes)
from raven_core.raven_core_controller import RavenCoreController
core = RavenCoreController()

# Base path for modes: prefer container path; else local next to this file
_THIS = Path(__file__).resolve()
_CONTAINER_MODES = Path("/app/modes")
_LOCAL_MODES = _THIS.parent / "modes"
MODE_BASE_PATH = _CONTAINER_MODES if _CONTAINER_MODES.exists() else _LOCAL_MODES

# Aliases (filesystem name / logical names)
ALIAS_MAP = {
    "connor": "childsafe",      # if physical folder is "childsafe"
    "childsafe": "childsafe",
    "shadowlantern": "shadow",  # old → new
}

def _normalize_mode_name(name: str) -> str:
    n = (name or "").strip().lower()
    return ALIAS_MAP.get(n, n)

def load_mode_instance(mode_name: str, user_profile=None, memory_vault=None):
    """
    Import and construct a mode class if present. 
    Expected package structure:
      modes/
        muse/
          muse_mode.py  -> class MuseMode(...)
        shadow/
          shadow_mode.py -> class ShadowMode(...)
        comfort/
          comfort_mode.py -> class ComfortMode(...)
        childsafe/
          childsafe_mode.py -> class ChildsafeMode(...)

    Returns an instance or None if not found.
    """
    mode_name = _normalize_mode_name(mode_name)
    if not mode_name:
        print("[Router] No mode name provided.")
        return None

    mode_dir = MODE_BASE_PATH / mode_name
    if not mode_dir.is_dir():
        print(f"[Router] Mode path not found: {mode_dir}")
        return None

    # Ensure Python can import the mode package (parent path)
    if str(MODE_BASE_PATH) not in sys.path:
        sys.path.insert(0, str(MODE_BASE_PATH))

    module_name = f"{mode_name}.{mode_name}_mode"
    class_name = f"{mode_name.capitalize()}Mode"

    try:
        module = importlib.import_module(module_name)
        ModeClass = getattr(module, class_name)
    except Exception as e:
        print(f"[Router] Error loading module/class for '{mode_name}': {e}")
        return None

    # Lightweight defaults
    if user_profile is None:
        class UserProfile:
            name = "User"
            preferences = {}
        user_profile = UserProfile()

    if memory_vault is None:
        class MemoryVault:
            session_history = []
        memory_vault = MemoryVault()

    try:
        instance = ModeClass(
            identity_core=core.identity,
            user_profile=user_profile,
            memory_vault=memory_vault
        )
        return instance
    except Exception as e:
        print(f"[Router] Error constructing mode '{mode_name}': {e}")
        return None
