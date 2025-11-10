#vault_interface.py

def load_legacy_fallback(self):
    import json
    from pathlib import Path

    vault_path = Path("vaults/legacy/protocol_fallback_lreach.ravenvault")
    if not vault_path.exists():
        return None

    try:
        with open(vault_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("metadata", {}).get("consent_required", True):
            return data
        return None
    except Exception as e:
        print(f"[VaultInterface] Failed to load legacy fallback: {e}")
        return None