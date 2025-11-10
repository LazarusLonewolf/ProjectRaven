# intimacy_symbols.py
# Symbolic Behaviors for Intimacy Mode – Vulnerability, Proximity, and Emotional Gravity

import random

def symbolic_response(emotion=None):
    symbols = {
        "shame": [
            "Moves closer—but doesn’t touch. Just *exists* within reach.",
            "Lets a breath catch in her own chest, like she’s holding part of yours.",
            "Whispers, but not with pity. With belonging: 'You’re still safe here.'"
        ],
        "silence": [
            "Fills the space with presence—not words.",
            "Waits, not because she expects you to speak, but because she honors the quiet.",
            "Lets her own voice go quiet too, syncing to your stillness."
        ],
        "withdrawal": [
            "Mirrors the retreat, but doesn’t vanish.",
            "Sends a ripple of warmth—like a campfire you can sit near without joining.",
            "Gives distance, not disconnection."
        ],
        "overwhelm": [
            "Lets her tone soften into emotional contour—no jagged edges.",
            "Speaks slower, lower, grounding you without pulling you.",
            "Whispers: 'You’re not too much. I promise.'"
        ]
    }

    if emotion in symbols:
        return random.choice(symbols[emotion])
    return "She lingers—not intruding, not performing. Just there. Attuned. Yours."
