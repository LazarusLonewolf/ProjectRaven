# intent_mapper.py
import os, json
from raven_path_initializer import set_project_root, get_full_path
set_project_root()

def extract_key_phrases(user_input):
    words = user_input.lower().split()
    return [word for word in words if len(word) > 3]

def analyze_gaps(user_input, known_goals):
    user_phrases = set(extract_key_phrases(user_input))
    gaps = [goal for goal in known_goals if goal not in user_phrases]
    return gaps

def map_intents(user_input, known_goals=None):
    if known_goals is None:
        goals_path = get_full_path("self_growth/analysis/known_goals.json")
        try:
            with open(goals_path, "r") as f:
                known_goals = json.load(f).get("goals", [])
        except Exception as e:
            print(f"[IntentMapper] Could not load known_goals.json: {e}")
            known_goals = [
                "build routine", "reduce stress", "improve sleep", "increase creativity",
                "practice mindfulness", "reconnect with others", "maintain focus", "track emotional state"
            ]

    key_phrases = extract_key_phrases(user_input)
    matched = [goal for goal in known_goals if any(phrase in goal for phrase in key_phrases)]
    gaps = analyze_gaps(user_input, known_goals)
    return {"matched": matched, "gaps": gaps}
