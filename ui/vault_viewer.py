# vault_viewer.py
# GUI Helper for Memory Vaults – Project_Raven

import os
import sys
import json
from pathlib import Path

# Dynamically locate Project_Raven root
def set_project_root():
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if parent.name == 'Project_Raven':
            sys.path.insert(0, str(parent))
            os.environ['PROJECT_RAVEN_ROOT'] = str(parent)
            break
    else:
        raise RuntimeError("Project_Raven root not found in path tree.")

set_project_root()

from utilities.path_refactor import get_full_path

def read_vault():
    try:
        vault_path = get_full_path("memory/vaults/session_vault.json")
        with open(vault_path, "r") as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"[VaultViewer] Error reading memory vault: {e}")
        return {}

if __name__ == "__main__":
    vault_data = read_vault()
    if vault_data:
        print("[VaultViewer] Current Session Memory:")
        for entry in vault_data.get("entries", []):
            print(f"- {entry}")
    else:
        print("[VaultViewer] No vault data available.")
