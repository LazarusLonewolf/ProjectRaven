# vault_interface.py — Raven Vault Access Layer | Project_Raven

import os
import json
from pathlib import Path
from raven_path_initializer import get_full_path

VAULT_ROOT = get_full_path("vaults")

def list_vault_files():
    vault_files = []
    for root, _, files in os.walk(VAULT_ROOT):
        for file in files:
            if file.endswith(".txt") or file.endswith(".md"):
                vault_files.append(os.path.join(root, file))
    return vault_files

def read_vault_file(relative_path):
    full_path = os.path.join(VAULT_ROOT, relative_path)
    if not os.path.exists(full_path):
        return None
    with open(full_path, 'r', encoding='utf-8') as file:
        return file.read()

def search_vault(query):
    matched_files = {}
    for file_path in list_vault_files():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if query.lower() in content.lower():
                    matched_files[file_path] = content
        except Exception as e:
            print(f"[WARN] Failed to read {file_path}: {e}")
    return matched_files

if __name__ == "__main__":
    print("[DEBUG] Listing all Raven Vault files...")
    for file in list_vault_files():
        print(file)
