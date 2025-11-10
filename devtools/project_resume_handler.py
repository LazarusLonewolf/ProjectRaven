# project_resume_handler.py

import json
from pathlib import Path

# Dynamically resolve the base path relative to this file
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_FILE = BASE_DIR / "projects.json"

def load_projects():
    if not PROJECTS_FILE.exists():
        return []

    try:
        with open(PROJECTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def get_project_by_name(project_name):
    projects = load_projects()
    for project in projects:
        if project.get("name", "").lower() == project_name.lower():
            return project
    return None

def list_active_projects():
    projects = load_projects()
    return [p for p in projects if p.get("status", "").lower() != "completed"]
