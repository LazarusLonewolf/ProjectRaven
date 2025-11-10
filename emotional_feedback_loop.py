# EFLL – Emotional Feedback Loop – Raven Core
# Purpose: Interpret, evaluate, and route emotional responses based on input, mode, and relational context.

import os
import sys
from raven_path_initializer import set_project_root
set_project_root()
import datetime
import json

from utilities.path_refactor import get_full_path

# Ethos-enhanced emotional processing
def load_raven_ethos(reference_path):
    try:
        with open(reference_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Failed to load ethos data: {e}")
        return ""

# File paths using dynamic resolution
RELATIONAL_MEMORY_PATH = get_full_path("relational_memory.json")
LOG_PATH = get_full_path("self_growth/memory/emotion_log.db")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAVEN_ETHOS_PATH = os.path.join(ROOT_DIR, "vaults", "raven_training_data.txt")
raven_ethos_data = load_raven_ethos(RAVEN_ETHOS_PATH)

# === Ethos-enhanced emotional processing ===
def apply_ethos_enrichment(emotion):
    if not raven_ethos_data:
        return emotion

    # Normalize for matching
    emotion_lower = emotion.strip().lower()

    # Simple contextual affirmation logic — pulls from ethos wording cues
    if emotion_lower in ["afraid", "nervous", "uncertain"]:
        if "courage" in raven_ethos_data.lower() or "keep going" in raven_ethos_data.lower():
            return "focused_caution"
    elif emotion_lower in ["sad", "down", "depressed"]:
        if "i keep moving forward" in raven_ethos_data.lower() or "resilient" in raven_ethos_data.lower():
            return "grieving_with_strength"
    elif emotion_lower in ["angry", "frustrated"]:
        if "i won’t give up on people" in raven_ethos_data.lower():
            return "frustrated_care"
    elif emotion_lower in ["lonely", "isolated"]:
        if "i know someone’s still out there" in raven_ethos_data.lower():
            return "longing_with_hope"

    return emotion
 
# === Emotion Keyword Map for Basic Detection ===
emotion_keywords = {
    "hard days": "resilience",
    "learned from": "gratitude",
    "sticks with you": "legacy",
    "felt proud": "pride",
    "felt alone": "grief",
    "carry with you": "loyalty",

    "happy": "joy",
    "joyful": "joy",
    "excited": "joy",
    "content": "peace",
    "grateful": "peace",

    "sad": "grief",
    "down": "grief",
    "depressed": "grief",
    "lonely": "grief",
    "mourning": "grief",
    "angry": "frustration",
    "frustrated": "frustration",
    "upset": "frustration",
    "irritated": "frustration",

    "anxious": "anxiety",
    "worried": "anxiety",
    "nervous": "anxiety",
    "overwhelmed": "anxiety",
    "stressed": "anxiety",

    "hopeful": "hope",
    "determined": "hope",
    "motivated": "hope",

    "ashamed": "shame",
    "guilty": "shame",
    "regret": "shame",

    "tired": "exhaustion",
    "burnt out": "exhaustion",
    "drained": "exhaustion",
    
    "proud": "pride",
    "accomplished": "pride",
    "fulfilled": "pride",
    "hopeful": "hope",
    "longing": "hope",
    "yearning": "hope",
    "ashamed": "shame",
    "remorseful": "shame",
    "sorry": "shame",
    "warm": "comfort",
    "safe": "comfort",
    "comforted": "comfort"
}
    
# === Basic Emotion Detection Function ===
def detect_emotion(input_text):
    lowered = input_text.lower()
    # Direct phrase cues before single keywords
    phrase_cues = {
        "hard days": "resilience",
        "something you learned": "gratitude",
        "sticks with you": "legacy",
        "what matters": "purpose"
    }
    for phrase, emotion in phrase_cues.items():
        if phrase in lowered:
            return emotion
    for keyword, emotion in emotion_keywords.items():
        if keyword in lowered:
            return emotion
    return "neutral"

class EmotionalFeedbackLoop:
    def __init__(self):
        self.log = []
        
    def detect_from_text(self, input_text):
        raw_emotion = detect_emotion(input_text)
        enriched = apply_ethos_enrichment(raw_emotion)
        self.log.append(enriched)
        return enriched
 
    def process_emotion(self, emotion):
        enriched = apply_ethos_enrichment(emotion)
        self.log.append(enriched)
        return enriched

def load_relational_memory():
    try:
        with open(RELATIONAL_MEMORY_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}

def log_emotional_event(source, intensity, category, mode, relational_state, notes=None):
    timestamp = datetime.datetime.now().isoformat()
    entry = {
        "timestamp": timestamp,
        "source": source,
        "intensity": intensity,
        "category": category,
        "mode": mode,
        "relational_state": relational_state,
        "notes": notes or ""
    }
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(entry) + "\n")
    except Exception:
        pass

def route_emotional_response(input_text, mode, identity):
    memory = load_relational_memory()
    tone = "neutral"
    intensity = "medium"
    category = "general"
    notes = ""

    if identity and identity.lower() in memory:
        bond = memory[identity.lower()]
        tone = bond.get("tone", "gentle")
        notes += f"Tone influenced by bond: {tone}. "

    if mode == "comfort":
        tone = "soothing"
        category = "reassurance"
    elif mode == "shadow":
        tone = "anchored"
        category = "stabilization"
    elif mode == "intimacy":
        tone = "present"
        category = "connection"
    elif mode == "child_safe":
        tone = "simple"
        category = "support"

    log_emotional_event(source=identity, intensity=intensity, category=category, mode=mode, relational_state=tone, notes=notes)
    return {
        "tone": tone,
        "category": category,
        "intensity": intensity,
        "notes": notes
    }
