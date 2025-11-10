# shadowlantern_memory_responses.py – Personality-Anchored Memory Callback Phrasing (Shadow Lantern Mode)

from raven_path_initializer import get_full_path
import random

SHADOWLANTERN_MEMORY_TEMPLATES = [
    "This reminds me of something we’ve faced before—would it help to look back?",
    "A deeper thread just surfaced. I can recall it if you want to walk through it.",
    "There's a memory lingering under the surface. You’re not alone if you want to face it.",
    "The weight of this moment echoes something we’ve held before. Should we revisit it?",
    "Sometimes shadows hold clarity. I’ve kept one tucked away, in case it matters now."
]

def get_shadowlantern_memory_callback(user_input=None, context=None):
    return random.choice(SHADOWLANTERN_MEMORY_TEMPLATES)
    
# --- Follow-up Generator for Shadow Mode ---
def shadow_followup_generator(session_context, emotion_tag):
    """
    Returns a follow-up prompt only if no direct emotion template exists and thread is weak.
    """
    if not session_context or not emotion_tag:
        return None

    fallback_prompts = {
        "neutral": "Want to explore something beneath the surface?",
        "unclear": "You don’t have to explain everything—but we can sit with it.",
        "sad": "Would it help to name what’s been weighing you down?",
        "bored": "Beneath boredom, there's usually hunger. Want to go looking?",
        "curious": "What made you curious just now?",
        "anxious": "Is the anxiety tied to something real—or imagined?",
        "resentment": "Is it something unresolved—or someone unspoken?",
    }

    return fallback_prompts.get(emotion_tag, None)    
