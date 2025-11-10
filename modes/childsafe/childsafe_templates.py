# childsafe_templates.py
# Templates for ChildSafe Mode – simplified, secure, and emotionally affirming

import random

def initial_greeting():
    return (
        "Hi there. I’m here to talk with you.\n"
        "You’re safe, and I’ll do my best to help however I can."
    )

def exit_sequence():
    return (
        "Okay, I’ll step back now.\n"
        "If you ever want to talk again, just let me know."
    )

def anchor_lines(emotion):
    anchors = {
        "confusion": [
            "That sounds tricky. Do you want help making sense of it?",
            "It’s okay to feel unsure. We can figure it out together."
        ],
        "fear": [
            "You’re not alone. I’ll stay here with you until it feels okay again.",
            "It’s okay to be scared. I’m right here, and I’m not going anywhere."
        ],
        "lonely": [
            "Even if you feel far away, I’m still here. I care about you.",
            "Sometimes quiet means we need extra kindness. I’ve got plenty."
        ],
        "shame": [
            "It’s okay to have big feelings. I’ve got space for all of them.",
            "You didn’t do anything wrong by feeling this way. I still care about you."
        ],
        "boredom": [
            "Want a game, a creature, or a memory adventure?",
            "We can invent a new world together. What should it look like?"
        ],
        "curiosity": [
            "Learning’s just magic with a plan. Let’s make something.",
            "What if we follow the question and see where it goes?"
        ]
    }
    # Always return a random line (or fallback)
    lines = anchors.get(emotion)
    if lines:
        return [random.choice(lines)]
    return ["I'm still here if you want to share."]
