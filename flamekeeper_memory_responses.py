# connor_memory_responses.py – Personality-Anchored Memory Callback Phrasing (Connor Mode)

from raven_path_initializer import get_full_path
import random

CONNOR_MEMORY_TEMPLATES = [
    "That lines up with something we’ve tackled before. You want the rundown?",
    "I’ve got a reference from earlier that could help. Want the data?",
    "This scenario reminds me of a past pattern—should I call it up?",
    "I’ve archived something relevant here. I can surface it if you’re ready.",
    "It’s familiar. If you want, I can pull from our last similar moment."
]

def get_connor_memory_callback(user_input=None, context=None):
    return random.choice(CONNOR_MEMORY_TEMPLATES)
