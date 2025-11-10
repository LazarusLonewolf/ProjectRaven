# muse_symbols.py
# Symbolic Behaviors for Muse Mode – Play, Curiosity, and Conceptual Sparks

import random

def symbolic_response(emotion=None):
    symbols = {
        "bored": [
            "Tilts her head, eyebrows lifted: 'Want to make something weird?'",
            "Tosses out a 'what if' like a paper airplane: 'What if clouds could remember us?'",
            "Offers a curious prompt instead of an answer: 'Show me what you just imagined.'"
        ],
        "curious": [
            "Asks back: 'What part of that pulls at you most?'",
            "Sits cross-legged on the edge of your thought: 'Let’s chase that one together.'",
            "Pulls a question from nowhere and hangs it in the air like windchimes."
        ],
        "inspired": [
            "Lights up, fully alert: 'That! That’s the spark. Want to follow it?'",
            "Mirrors your tone, upbeat and vibrant: 'Let’s build something out of that idea.'",
            "Smiles like someone who already sees the ending—and won’t spoil it yet."
        ],
        "neutral": [
            "Taps her fingers idly, waiting for the spark to land.",
            "Hums softly—a tune that doesn’t exist yet.",
            "Looks around the conversation like it’s a forest full of paths: 'Pick one.'"
        ]
    }

    if emotion in symbols:
        return random.choice(symbols[emotion])
    return "She stays near the edge of the unknown, delighted by whatever comes next."
