import os
import json
import shutil
from datetime import datetime
from pathlib import Path

from raven_path_initializer import set_project_root, get_full_path
set_project_root()

JOURNAL_LOGS_DIR = Path(get_full_path("self_growth/journals/logs"))
REFLECTIONS_DIR = Path(get_full_path("self_growth/journals/reflection/reflections"))
VAULT_DIR = Path(get_full_path("vaults/data"))

# Load Raven's ethos
def load_raven_ethos(reference_path):
    try:
        with open(reference_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Could not load Raven ethos: {e}")
        return ""

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAVEN_ETHOS_PATH = os.path.join(ROOT_DIR, "vaults", "raven_training_data.txt")
    raven_ethos_data = load_raven_ethos(RAVEN_ETHOS_PATH)

def ethos_enrich(text):
    if not raven_ethos_data:
        return text
    if "tired" in text.lower() and "but I keep going" in raven_ethos_data.lower():
        return text + " Still, I keep going—because that’s what I do."
    if "hopeless" in text.lower() and "light returns" in raven_ethos_data.lower():
        return text + " But somewhere deep down, I know the light returns."
    return text


class ReflectiveJournalManager:
    def __init__(self, reflection_path):
        self.reflection_path = reflection_path

    def save_reflection(reflection_text):
        enriched = ethos_enrich(reflection_text)
        REFLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = REFLECTIONS_DIR / f"reflection_{timestamp}.txt"
        with open(file_path, "w") as f:
            f.write(enriched)
        return file_path

def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def backup_context_history():
    context_file = Path(get_full_path("self_growth/journals/reflection/context_history.json"))
    backup_dir = Path(get_full_path("self_growth/journals/reflection/context_backups"))
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"context_backup_{timestamp}.json"
    shutil.copy(context_file, backup_file)
    return backup_file

def save_reflection(reflection_text):
    REFLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = REFLECTIONS_DIR / f"reflection_{timestamp}.txt"
    with open(file_path, "w") as f:
        f.write(reflection_text)
    return file_path

def log_journal_entry(content):
    JOURNAL_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = JOURNAL_LOGS_DIR / "daily_log.txt"
    with open(log_file, "a") as f:
        f.write(f"{timestamp} — {content}\n")
