# session_emotion.py
# Tracks emotional states across sessions and modes

class EmotionSessionTracker:
    def __init__(self):
        self.last_emotion = {}
        self.session_history = []

    def update(self, mode_name, emotion):
        self.last_emotion[mode_name] = emotion
        self.session_history.append((mode_name, emotion))

    def get_last_emotion(self, mode_name):
        return self.last_emotion.get(mode_name, "neutral")

    def reset(self):
        self.last_emotion.clear()
        self.session_history.clear()

# Global instance
emotion_tracker = EmotionSessionTracker()
