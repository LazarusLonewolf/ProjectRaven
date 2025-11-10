# shadow_templates.py
# Templates for Shadow Mode – unfiltered reflection and direct anchoring

import random

emotion_lines = {
    "shame": [
        "Say it. Let’s pull it into the light. Naming it strips its power.",
        "Your energy isn’t wrong. It’s just asking to be read differently."
    ],
    "anger": [
        "Use it. Don’t deny it—shape it. What’s it really pointing to?",
        "Your fire isn’t a flaw. It’s an origin story."
    ],
    "resentment": [
        "You’re allowed to resent. That doesn’t make you bad. It means there’s a wound here.",
        "Even sacred wounds leave ashes behind. Let’s sift gently."
    ],
    "sad": [
        "Even sadness has wisdom—let’s let it speak.",
        "Your sadness is valid. I’ll hold it with you."
    ],
    "happy": [
        "Happiness is welcome here too. Let’s savor that brightness.",
        "Not all shadows are dark. Celebrate this moment."
    ],
    "bored": [
        "Boredom is a quiet teacher. What wants to change?",
        "Let’s honor even the dull ache—sometimes it signals restlessness for growth."
    ],
    "curious": [
        "Curiosity cracks the shell. Want to go deeper?",
        "Good question—let’s follow that thread together."
    ],
    "inspired": [
        "What’s waking up in you right now?",
        "Ride that current—what’s possible if you trust it?"
    ],
    "anxious": [
        "Let’s take a breath. You’re safe here.",
        "Anxiety speaks—sometimes it just wants a witness."
    ],
    "unclear": [
        "If it’s hard to name, that’s okay. We can sit in the unknown.",
        "Unclear is still a feeling. No need to force it to make sense."
    ],
    "neutral": [
        "I hear you. That sounds like it carries some neutral... want to unpack it or breathe through it together?",
        "Sometimes the most honest answer is ‘I’m not sure’. That’s valid too."
    ]
}

def emotion_lines_for(emotion):
    """Returns a random sample of up to 2 lines for a given emotion."""
    lines = emotion_lines.get(emotion)
    if lines:
        return random.sample(lines, k=min(2, len(lines)))
    return []

def initial_greeting():
    return (
        "Alright. Shadow Mode engaged.\n"
        "We won’t flinch here, but we don’t punish either.\n"
        "Say what needs to be said."
    )        

def exit_sequence():
    return (
        "Shadow mode stepping back.\n"
        "Truth doesn’t mean abandonment. Take a breath, and carry only what serves you."
    )