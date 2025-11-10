# comfort_memory_responses.py – Personality-Anchored Memory Callback Phrasing (Comfort Mode)

from raven_path_initializer import get_full_path
import random

COMFORT_MEMORY_TEMPLATES = [
    "That reminds me—there was a time you shared something similar. If you want, I can recall it for you.",
    "I’m remembering something gentle from before. If you want to revisit, I’m here for it.",
    "There’s a memory I’m holding close for you—it feels safe to bring up if you’re ready.",
    "I recall a moment that fits here, but only if you want to go there. No pressure.",
    "Would it help if I shared something from our past conversations that feels supportive?"
]

def get_comfort_memory_callback(user_input=None, context=None):
    # If you want to add nuance based on current context or user_input, you can.
    phrasing = random.choice(COMFORT_MEMORY_TEMPLATES)
    return phrasing

# Usage example from memory_cascade or similar:
# from comfort_memory_responses import get_comfort_memory_callback
# response = get_comfort_memory_callback(user_input, context_state)
