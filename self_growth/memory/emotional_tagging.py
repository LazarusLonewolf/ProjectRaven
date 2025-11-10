# emotional_tagging.py
# Expanded emotion analysis with ADHD-conscious and ambiguous emotion phrasing

import os
import json
from pathlib import Path
from raven_path_initializer import BASE_PATH
from raven_path_initializer import get_full_path
BASE_RAVEN_PATH = Path(get_full_path("."))
...
training_path = BASE_RAVEN_PATH / "vaults" / "raven_training_data.txt"

BASE_RAVEN_PATH = os.environ.get(
    "RAVEN_ROOT",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

# --- robust base path resolution ---
try:
    # prefer the project initializer if available
    from raven_path_initializer import get_full_path
    BASE_RAVEN_PATH = get_full_path("")  # project root (…/Raven)
except Exception:
    # fallback to env or relative to this file
    BASE_RAVEN_PATH = os.environ.get(
        "RAVEN_ROOT",
        str(Path(__file__).resolve().parents[3])  # …/Raven
    )

class EmotionalTagger:
    def __init__(self, base_path: str | None = None):
        def __init__(self, _root_path=None):
        self.root = _root_path or BASE_RAVEN_PATH
        self.raven_training_reference = self._load_training_reference()
        self.base_path = base_path
        self.tags = {}
       
    def _load_training_reference(self):
        training_path = os.path.join(BASE_RAVEN_PATH, "vaults", "raven_training_data.txt")
        try:
            with open(training_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
            
    def analyze(self, text: str) -> str:
        t = (text or "").lower()
        if any(k in t for k in ("overwhelm", "tired", "can't focus", "anxious", "sad", "down")):
            return "overwhelm"
        if any(k in t for k in ("angry", "mad", "frustrat")):
            return "frustration"
        if any(k in t for k in ("idea", "story", "create", "brainstorm")):
            return "curious"
        return "neutral"

    def tag_emotion(self, entry_id, emotion):
        if not self._validate_emotion(emotion):
            raise ValueError("Invalid emotion format")

        self.tags[entry_id] = {
            "emotion": emotion,
            "reference_ethos": self._derive_reference_emotion(emotion)
        }

    def _derive_reference_emotion(self, emotion):
        if not self.raven_training_reference:
            return "Reference data not available"

        emotion_keywords = {
            "happy": ["happy", "joy", "glad", "excited", "pleased"],
            "sad": ["sad", "unhappy", "depressed", "down", "blue"],
            "angry": ["angry", "mad", "furious", "irritated", "annoyed"],
            "anxious": [
                "anxious", "nervous", "worried", "afraid", "scared", "overwhelmed",
                "too many tabs open", "my brain won't stop", "i'm all over the place",
                "i keep forgetting", "can't sit still"
            ],
            "bored": [
                "bored", "restless", "dull", "meh", "tired", "can't focus",
                "can't concentrate", "i can't sit still", "i'm distracted"
            ],
            "curious": ["curious", "interested", "wondering", "inquisitive"],
            "inspired": ["inspired", "creative", "motivated", "driven", "hopeful"],
            "unclear": [
                "i don't know how i feel", "i can't describe it", "it's just weird",
                "hard to explain", "everything at once", "nothing feels right",
                "i don't know", "i have no idea"
            ],
            "neutral": []
        }

        match = emotion_keywords.get(emotion.lower())
        if match is not None:
            return match
        else:
            return "Emotion not explicitly mapped, using neutral baseline."

    def get_tag(self, entry_id):
        return self.tags.get(entry_id, None)

    def save_tags(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.tags, file, indent=2)

    def _validate_emotion(self, emotion):
        valid_emotions = {
            "happy", "sad", "angry", "anxious", "bored",
            "curious", "inspired", "unclear", "neutral"
        }
        return emotion.lower() in valid_emotions

