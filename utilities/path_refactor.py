# path_refactor.py
# "$RAVEN_HOME/utilities/path_refactor.py"

import os
import re
from importlib import import_module

from raven_path_initializer import base_raven_path  # single source of truth

def _fallback_get_full_path(rel: str) -> str:
    import os
    return os.path.abspath(rel)
    
try:
    rpi = import_module("raven_path_initializer")
    get_full_path    = getattr(rpi, "get_full_path", _fallback_get_full_path)
    set_project_root = getattr(rpi, "set_project_root", lambda: None)
    initialize_paths = getattr(rpi, "initialize_paths", lambda: None)
except Exception:
    # If initializer isn't importable yet, still provide callables.
    get_full_path    = _fallback_get_full_path
    set_project_root = lambda: None
    initialize_paths = lambda: None

# Patterns to catch hardcoded paths
path_patterns = [
    r'["\']\/app\/',          # "/app/"
    r'["\']\/aeris\/',        # "/aeris/"
    r'["\']\/raven_mail\/?',  # "/raven_mail"
]

# Replacement format
def replace_path(match):
    matched = match.group(0)
    if "/app/" in matched:
        return f'os.path.join(BASE_PATH_VAR, '
    elif "/aeris/" in matched:
        return f'os.path.join(BASE_PATH_VAR, "aeris", '
    elif "/raven_mail" in matched:
        return f'os.path.join(BASE_PATH_VAR, "raven_mail")'
    return matched

# Walk through files and apply replacements
def refactor_paths(target_dir):
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.py', '.sh')):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content
                for pattern in path_patterns:
                    content = re.sub(pattern, replace_path, content)

                if content != original:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated: {file_path}")
                    
def get_full_path(relative_path):
    """
    Dynamically builds an absolute path using RAVEN_HOME or fallback /app.
    """
    base = os.getenv("RAVEN_HOME", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
    return os.path.join(base_raven_path, relative_path)
  
def get_vault_paths():
    """
    Returns a list of full file paths inside the Vaults directory.
    """
    vault_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "vaults"))
    vault_files = []

    for root, _, files in os.walk(vault_root):
        for file in files:
            full_path = os.path.join(root, file)
            vault_files.append(full_path)

    return vault_files
                  
if __name__ == "__main__":
    target_directory = os.path.abspath("./app")  # Adjust path if needed
    refactor_paths(target_directory)