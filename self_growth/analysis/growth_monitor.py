# growth_monitor.py – Raven Analysis Layer | Project_Raven

import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from raven_path_initializer import set_project_root, get_full_path
set_project_root()


import os

# Load Raven's ethos data
def load_raven_ethos(reference_path):
    try:
        with open(reference_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Failed to load ethos data: {e}")
        return ""

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAVEN_ETHOS_PATH = os.path.join(ROOT_DIR, "vaults", "raven_training_data.txt")
raven_ethos_data = load_raven_ethos(RAVEN_ETHOS_PATH)

# Adjust sentiment score based on ethos pattern matches
def ethos_enhanced_score(text, base_score):
    if not raven_ethos_data:
        return base_score
    lower_text = text.lower()
    if "trying anyway" in lower_text or "i keep going" in lower_text:
        if "resilient" in raven_ethos_data.lower() or "keep showing up" in raven_ethos_data.lower():
            return min(base_score + 0.2, 1.0)
    if "it's hard" in lower_text and "learning" in raven_ethos_data.lower():
        return min(base_score + 0.1, 1.0)
    return base_score

class GrowthMonitor:
    def __init__(self):
        self.path = get_full_path("self_growth/analysis/growth_data.json")
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return {"entries": [], "score": 0}
        with open(self.path, "r") as f:
            return json.load(f)

    def update_growth(self, feedback):
        entry = {
            "feedback": feedback,
            "score": self._score_feedback(feedback)
        }
        self.data["entries"].append(entry)
        self.data["score"] += entry["score"]
        self._save()

    def _score_feedback(self, feedback):
        if "learned" in feedback:
            return 3
        if "struggled" in feedback:
            return 1
        if "mastered" in feedback:
            return 5
        return 2

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    def analyze_progress(self):
        if not self.data["entries"]:
            return "No growth data yet."
        avg_score = self.data["score"] / len(self.data["entries"])
        return f"Growth trajectory is forming. Current average: {avg_score:.2f}."

    def suggest_upgrades(self):
        if self.data["score"] < 20:
            return "Consider reinforcing foundational logic patterns."
        if self.data["score"] < 50:
            return "Introduce adaptive memory training exercises."
        return "Growth is solid. Open next development gate."

