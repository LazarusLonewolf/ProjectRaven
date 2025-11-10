# project_progress_tracker.py

import os
import csv
import json
from datetime import datetime
from pathlib import Path

# Dynamic directory resolution
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CSV_FILE_PATH = OUTPUT_DIR / "project_progress_log.csv"
PROJECTS_FILE = OUTPUT_DIR / "projects.json"

def log_project_progress(project_name, status, notes=""):
    """Logs project progress to CSV."""
    timestamp = datetime.now().isoformat()
    row = [timestamp, project_name, status, notes]

    file_exists = CSV_FILE_PATH.exists()

    with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Project Name", "Status", "Notes"])
        writer.writerow(row)

    return str(CSV_FILE_PATH)

def get_latest_entries(limit=5):
    """Returns the latest entries from the CSV log."""
    if not CSV_FILE_PATH.exists():
        return []

    with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
        lines = file.readlines()

    return lines[-limit:] if len(lines) > limit else lines

def update_project_status(project_name, new_status):
    """Updates or creates a project status entry in the JSON file."""
    projects = {}
    if PROJECTS_FILE.exists():
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            try:
                projects = json.load(f)
            except json.JSONDecodeError:
                projects = {}

    projects[project_name] = {
        "status": new_status,
        "last_updated": datetime.now().isoformat()
    }

    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=4)

    return str(PROJECTS_FILE)

def load_projects():
    """Loads all project statuses from the JSON file."""
    if not PROJECTS_FILE.exists():
        return {}

    with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
