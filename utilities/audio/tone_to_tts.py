# tone_to_tts.py
# Maps emotional tones to TTS voice modulation parameters (Piper, Onnx, etc.)

def get_tts_settings(emotion):
    tone_map = {
        "neutral":    {"pitch": 1.0, "speed": 1.0, "emotion": "neutral"},
        "shame":      {"pitch": 0.9, "speed": 0.85, "emotion": "soft"},
        "overwhelm":  {"pitch": 1.05, "speed": 0.9, "emotion": "concerned"},
        "silence":    {"pitch": 0.8, "speed": 0.75, "emotion": "gentle"},
        "withdrawal": {"pitch": 0.85, "speed": 0.8, "emotion": "careful"},
        "distress":   {"pitch": 1.1, "speed": 0.9, "emotion": "urgent"},
        "sadness":    {"pitch": 0.9, "speed": 0.85, "emotion": "mournful"},
        "anxiety":    {"pitch": 1.1, "speed": 1.05, "emotion": "tense"},
        "anger":      {"pitch": 1.2, "speed": 1.0, "emotion": "firm"},
        "curious":    {"pitch": 1.15, "speed": 1.1, "emotion": "inquisitive"},
        "inspired":   {"pitch": 1.25, "speed": 1.15, "emotion": "bright"},
        "bored":      {"pitch": 0.95, "speed": 0.95, "emotion": "flat"}
    }

    return tone_map.get(emotion, tone_map["neutral"])
