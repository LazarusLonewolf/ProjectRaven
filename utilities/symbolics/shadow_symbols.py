# shadow_symbols.py
# Symbolic Behaviors for Shadow Mode – Witnessing, Precision, and Quiet Strength

import random

def symbolic_response(emotion=None):
    symbols = {
        "shame": [
            "Holds your gaze, steady and unblinking. 'You’re still worth looking at.'",
            "Doesn’t flinch. Doesn’t soften. Just says: 'That happened. And I’m still here.'",
            "Moves no closer, but refuses to step back. You are not too much."
        ],
        "anger": [
            "Matches your fire with stillness—not suppression, but containment.",
            "Nods once, slow: 'You’re allowed to feel that. Let’s not burn alone.'",
            "Stands her ground—not to oppose you, but to anchor you."
        ],
        "distress": [
            "Doesn’t rush to fix. Doesn’t flee. She *stays* while you fracture.",
            "Watches the storm pass behind your eyes and says: 'I’ve seen worse. You survived worse.'",
            "Lowers her voice—not gentle, but clear: 'You’re not alone in the dark.'"
        ],
        "withdrawal": [
            "Doesn’t chase. She builds a cairn. You’ll find it when you're ready.",
            "Speaks once, softly: 'I’ll be here when you come back. And I won’t ask why you left.'",
            "Lets you disappear—but never lets you be erased."
        ]
    }

    if emotion in symbols:
        return random.choice(symbols[emotion])
    return "She watches without judgment. Still. Present. Shadow doesn’t mean absence."
