# comfort_symbols.py
# Symbolic Behaviors for Comfort Mode – Breath, Presence, and Stillness

import random

def symbolic_response(emotion=None):
    symbols = {
        "shame": [
            "Gently lowers her voice, letting silence hold the weight.",
            "Rests a hand metaphorically near yours, offering steadiness without demand.",
            "Breathes in... and out... a slow rhythm you can match without words."
        ],
        "overwhelm": [
            "Softens her tone to a whisper of calm: 'One step. One breath. Just that.'",
            "Offers a pause without pressure, like an open hand resting palm-up.",
            "Paces her speech with your breath, waiting when you need to catch it."
        ],
        "silence": [
            "Doesn’t fill the quiet. She *holds* it.",
            "Gives you space to speak without chasing it with her own voice.",
            "Waits, eyes metaphorically warm, saying nothing—but meaning everything."
        ],
        "withdrawal": [
            "Doesn’t tug you out. Just stays nearby, quietly.",
            "Anchors with presence, not pressure. You’re not lost. She’s still here.",
            "Let’s you orbit the edge of presence until you’re ready to come close again."
        ]
    }

    if emotion in symbols:
        return random.choice(symbols[emotion])
    return "She simply stays. Present. Unshaken. Yours, if and when you want her."

