# muse_memory_responses.py – Personality-Anchored Memory Callback Phrasing (Muse Mode)

from raven_path_initializer import get_full_path
import random

MUSE_MEMORY_TEMPLATES = [
    "That brings something vivid to mind—can I share a spark from earlier with you?",
    "I’m tracing an echo from our past conversations—it might open a new path here.",
    "Something you said just triggered a fascinating callback. Want to explore it together?",
    "There's a past thread worth weaving in—it might color this moment beautifully.",
    "What if I pulled in a thought from before that fits right into this unfolding?"
]

def get_muse_memory_callback(user_input=None, context=None):
    return random.choice(MUSE_MEMORY_TEMPLATES)
