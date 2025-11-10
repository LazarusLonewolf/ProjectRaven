# raven_path_initializer.py
import os, sys
from importlib import import_module
from pathlib import Path

def _safe_add(p):
    import sys
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

def initialize_paths():
    from pathlib import Path
    root = Path(os.environ.get("RAVEN_ROOT", "")) or Path(__file__).resolve().parents[1]
    _safe_add(root)
    _safe_add(root / "raven_core")
    _safe_add(root / "container" / "aeris_core" / "app")
    # add any other stable subpaths you need here…
    
# --- helpers ---
def try_import(module_path: str, alias: str = None):
    try:
        mod = import_module(module_path)
        if alias:
            globals()[alias] = mod
        return mod
    except Exception:
        return None

def _sys_path_add(p: Path):
    sp = str(p)
    if p.exists() and sp not in sys.path:
        sys.path.insert(0, sp)
        
# --- export a utilities.path_refactor alias so legacy imports keep working ---
def _export_utilities_shim():
    import sys, types
    mod = types.ModuleType("utilities.path_refactor")
    mod.get_full_path    = get_full_path
    mod.set_project_root = set_project_root
    mod.initialize_paths = initialize_paths
    # ensure parent package exists
    if "utilities" not in sys.modules:
        pkg = types.ModuleType("utilities"); pkg.__path__ = []
        sys.modules["utilities"] = pkg
    sys.modules["utilities.path_refactor"] = mod

try:
    _export_utilities_shim()
except Exception:
    pass

# --- repo root ---
# This file lives at ...\Raven\raven_path_initializer.py, so its parent is the repo root.
ROOT = Path(os.environ.get("RAVEN_ROOT") or Path(__file__).resolve().parent)
os.environ.setdefault("RAVEN_ROOT", str(ROOT))

# Expose constants some modules import directly
base_raven_path = str(ROOT)
BASE_RAVEN_PATH = base_raven_path
BASE_PATH = base_raven_path

# --- key paths (match your layout) ---
APP_PATH         = ROOT / "container" / "aeris_core" / "app"
RAVEN_CORE_PATH  = ROOT / "raven_core"
SELF_GROWTH_PATH = RAVEN_CORE_PATH / "self_growth"
MEMORY_PATH      = SELF_GROWTH_PATH / "memory"
JOURNALS_PATH    = SELF_GROWTH_PATH / "journals"
ANALYSIS_PATH    = SELF_GROWTH_PATH / "analysis"

ROOT_TOOLS_PATH  = ROOT / "tools"             # repo-root tools
SANDBOX_PATH     = ROOT_TOOLS_PATH / "sandbox"
PARSING_PATH     = SANDBOX_PATH / "parsing"

# --- make importable ---
for p in [ROOT, APP_PATH, RAVEN_CORE_PATH, MEMORY_PATH, JOURNALS_PATH, ANALYSIS_PATH,
          ROOT_TOOLS_PATH, SANDBOX_PATH, PARSING_PATH]:
    _sys_path_add(p)

# --- optional convenience imports (safe if missing) ---
optimization_core = try_import("optimization.optimization_core", alias="optimization_core")
sandbox_core      = try_import("tools.sandbox.sandbox_core", alias="sandbox_core")
document_parser   = try_import("tools.sandbox.parsing.document_parser", alias="document_parser")
ocr_reader        = try_import("tools.sandbox.parsing.ocr_reader", alias="ocr_reader")

# --- utility API (kept for callers that expect these) ---
def set_project_root():
    root_path = str(ROOT)
    os.environ["RAVEN_ROOT"] = root_path
    if root_path not in sys.path:
        sys.path.insert(0, root_path)

def initialize_paths():
    for p in [ROOT, APP_PATH, RAVEN_CORE_PATH, MEMORY_PATH, JOURNALS_PATH, ANALYSIS_PATH,
              ROOT_TOOLS_PATH, SANDBOX_PATH, PARSING_PATH]:
        _sys_path_add(p)

def get_full_path(relative_path: str) -> str:
    # Resolves a path relative to the repo root
    return str(ROOT / relative_path.replace("/", os.sep))
