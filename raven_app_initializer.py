# raven_app_initializer.py

import os
import sys
import importlib
from pathlib import Path
from raven_path_initializer import initialize_paths

# --- Load path refactor and initializer first ---
from container.aeris_core.app.utilities import path_refactor
import raven_path_initializer as rpi


# Ensure environment paths are set
rpi.set_project_root()

# Optional: verify all core dirs are in sys.path
required_paths = [
    rpi.RAVEN_CORE_PATH,
    rpi.MEMORY_PATH,
    rpi.JOURNALS_PATH,
    rpi.ANALYSIS_PATH
]
for p in required_paths:
    if str(p) not in sys.path:
        sys.path.append(str(p))

print(f"[Raven Init] Root set to {os.environ.get('RAVEN_ROOT')}")

# Initialize dynamic paths
initialize_paths()

# Define base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
TOOLS_DIR = os.path.join(ROOT_DIR, 'tools')

# Preload core tools
TOOL_MODULES = {
    'sandbox_core': 'sandbox.sandbox_core',
    'document_parser': 'sandbox.parsing.document_parser',
    'ocr_reader': 'sandbox.parsing.ocr_reader',
    'optimization_core': 'optimization.optimization_core',
    'sandbox_history': 'sandbox.sandbox_history',  # NEW
    # Add more tool references here as needed
}

# Global tool registry
loaded_tools = {}

for tool_name, module_path in TOOL_MODULES.items():
    try:
        module = importlib.import_module(module_path)
        loaded_tools[tool_name] = module
        print(f"[INIT] Loaded tool: {tool_name} from {module_path}")
    except Exception as e:
        print(f"[INIT] Failed to load {tool_name} from {module_path} — {e}")

# Avatar boot stub (visuals not yet supported)
AVATAR_DIR = os.path.join(TOOLS_DIR, 'avatar')
if not os.path.exists(AVATAR_DIR):
    print("[INIT] Avatar system skipped — visual environment inactive.")
else:
    print("[INIT] Avatar system detected, but not initialized.")

# Export for Raven system-wide use
def get_tool(tool_name):
    return loaded_tools.get(tool_name, None)
    