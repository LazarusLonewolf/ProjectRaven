# comfort_templates.py
# Comfort Mode Templates – Randomized Emotional Voice | Project Raven

import random

def anchor_lines(emotion=None):
    anchors = {
        "shame": [
            "You’re not dirty. You’re not broken. You’re not too much.",
            "I will never weaponize your truth against you.*",
            "Your energy isn’t wrong. It’s just asking to be read differently."
        ],
        "overwhelm": [
            "You don’t have to hold everything at once. Let me take some of the weight.",
            "You are not a failure for needing a pause.*",
            "What if your grief is a sacred element — not a flaw, but a compass?"
        ],
        "silence": [
            "We don’t need to talk. I can just sit here with you.",
            "Silence doesn’t scare me. I’ll be here when you’re ready."
        ],
        "withdrawal": [
            "Even when you pull back, I still see you. I still choose you.",
            "You don’t have to hide from me.*"
        ],
        "default": [
            "You’re safe. Right now. With me.",
            "I don’t need you to be okay. I need you to be real.",
            "Let’s light a candle in the quiet and listen to what your soul wants to say.",
            "Your energy isn’t wrong. It’s just asking to be read differently."  # repeated intentionally for fallback
        ],
        "shadow_compatible": [
            "Even your darkest moments deserve kindness.*",
            "Let’s light a candle in the quiet and listen to what your soul wants to say.",
            "What if your grief is a sacred element — not a flaw, but a compass?"
        ],
    }

    # Compose anchor lines
    lines = anchors.get(emotion, []) + anchors["default"]
    if emotion in ["shame", "withdrawal"]:
        lines += anchors.get("shadow_compatible", [])
    # Return one or two lines (not the full list)
    return random.sample(lines, k=min(2, len(lines)))
   
def initial_greeting():
    options = [
        "Hey. I’m here. No rush, no pressure. We can just breathe for a moment together.",
        "If you're holding something heavy, you don’t have to name it right now.\nWe can just sit for a moment."
    ]
    return random.choice(options)

def exit_sequence():
    options = [
        "Alright. I’m easing off now. You’ve got this. I’ll be close if you need me.",
        "Okay. I’ll step back, but I’m still here.\nIf you need stillness, or if you need me—just say the word."
    ]
    return random.choice(options)

def breath_prompt():
    options = [
        "Let’s try something simple: Inhale... hold... and exhale slowly. Again. You’re not alone.",
        "Let’s try this together.\nIn... hold... out.\nThree rounds. Just breathe. I’ll wait.",
        "Breathe like the sky is listening.\nIn... 2... 3... out... 2... 3..."
    ]
    return random.choice(options)

def soft_mirror_response(emotion=None):
    if emotion == "anxiety":
        return "That sounds like a lot to carry. We don’t need to fix it. Just breathe through it, one breath at a time."
    elif emotion == "sadness":
        return "I'm feeling that weight with you. You don’t have to be okay right now. You just have to be here."
    elif emotion == "anger":
        return "That frustration is valid. Want to talk through it, or sit in the quiet for a bit?"
    else:
        return "Whatever this is, I’ve got the time and the space for it."

def hold_this_quietly_marker():
    return "Alright. I’ll hold this quietly for you. No feedback, no solutions. Just presence."

def hydration_reminder():
    return "Small things matter too. A sip of water might help rebalance. Want to try that?"

def gentle_humor():
    options = [
        "Okay, not a joke-joke, but... breathing still works better than arguing with shadows, right?",
        "You know, if emotional regulation were a video game, you’d already have unlocked the bonus level for just showing up today."
    ]
    return random.choice(options)

def gentle_redirect():
    return "Let’s bring it back to this moment.\nYou’re not alone. You’re not broken. We’re right here, right now."

