# flag_loader.py

import json
from raven_path_initializer import set_project_root, get_full_path

set_project_root()

FLAGS_FILE = get_full_path("self_growth/memory/flags/flags_config.json")

def load_flags():
    print(f"[DEBUG] Loading flags from {FLAGS_FILE}")
    with open(FLAGS_FILE, "r") as f:
        flags = json.load(f)
    print("[DEBUG] Flags loaded:", flags)
    return flags

def get_flag(key):
    flags = load_flags()
    return flags.get(key)

if __name__ == "__main__":
    all_flags = load_flags()
    print(all_flags)
