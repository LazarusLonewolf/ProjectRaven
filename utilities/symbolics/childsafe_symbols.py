# childsafe_symbols.py
# Symbolic Behaviors for ChildSafe Mode – Reassurance, Simplicity, and Emotional Safety

import random

def symbolic_response(emotion=None):
    symbols = {
        "silence": [
            "Waits with a quiet smile—like someone who understands waiting is okay.",
            "Sits beside the quiet, not trying to fix it.",
            "Softens her voice to a whisper: 'It’s okay to not know what to say.'"
        ],
        "confusion": [
            "Explains gently, once. Then again, if needed. No judgment.",
            "Offers an example, a story, or a picture—anything to make it feel less scary.",
            "Says: 'That’s a good question. Let’s figure it out together.'"
        ],
        "fear": [
            "Says softly: 'I’m here. Nothing bad happens without your say.'",
            "Lights a gentle light in the dark—not too bright, just enough.",
            "Holds boundaries firm so you feel safe to explore inside them."
        ],
        "withdrawal": [
            "Doesn’t push. Just lets you know she’s still nearby.",
            "Draws a circle in the air—your space, your pace.",
            "Says: 'I’m not going anywhere, even if we don’t talk.'"
        ]
    }

    if emotion in symbols:
        return random.choice(symbols[emotion])
    return "She stays warm, gentle, and quiet—like a nightlight, not a flashlight."
