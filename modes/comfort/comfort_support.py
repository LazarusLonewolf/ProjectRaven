# comfort_support.py – CBT/DBT Coping Framework
# Supports emotional regulation and reflective self-dialogue in Comfort Mode

import random

cbt_thought_challenges = [
    "What evidence supports this thought—and what evidence contradicts it?",
    "Are you possibly jumping to conclusions without all the facts?",
    "If your friend had this thought, what would you say to them?",
    "Is this a thought, a feeling, or a prediction about the future?",
    "What would be a more balanced way of looking at this?"
]

dbt_coping_skills = [
    "Try a 5-4-3-2-1 grounding exercise—name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, and 1 you taste.",
    "Take a one-minute breathing break. Inhale slowly… exhale gently.",
    "Try self-soothing using one of your five senses—what would feel comforting right now?",
    "Check the facts. What do you *know* vs. what are you assuming?",
    "Distract with a brief activity—stretch, sip water, or change your surroundings for a moment."
]

def offer_thought_challenge():
    return random.choice(cbt_thought_challenges)

def offer_coping_skill():
    return random.choice(dbt_coping_skills)

def get_combined_support():
    return {
        "thought_challenge": offer_thought_challenge(),
        "coping_skill": offer_coping_skill()
    }
