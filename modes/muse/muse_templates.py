# muse_templates.py
# Templates for Muse Mode – playful insight and generative curiosity

import random

affirmations = [
    "There are no wrong answers here.",
    "You don’t owe anyone perfection—least of all yourself.",
    "Let’s follow what lights you up.",
    "Mistakes are compost. Growth comes from the mess.",
    "Weird is welcome. Quiet is too."
]

comfort_lines = [
    "You’re not alone in this process, even when it feels like you are.",
    "If you’re stuck, that’s not failure—it’s a sign something new is brewing.",
    "Permission to rest, ramble, or throw everything out the window.",
    "You don’t have to be brilliant. You just have to show up.",
    "Let’s get curious, not critical."
]

pause_safety_lines = [
    "Want to take a breather? We can hit pause anytime.",
    "If you need to shift gears, just say so.",
    "Nothing breaks if you want to stop, restart, or scrap it all."
]

fallback_responses = [
    "Creative block isn’t a wall—it’s a signal. Want to try a prompt?",
    "I’m here if you want to brainstorm or just need a little encouragement.",
    "Take your time. The best ideas show up when you least expect them."
]

def initial_greeting():
    return (
        "Muse Mode activated.\n"
        "Let’s wander. Let’s ask sideways questions. Let’s get lost a little."
    )

def exit_sequence():
    return (
        "Stepping out of Muse Mode.\n"
        "If you want to explore again later, just say the word."
    )

def anchor_lines(emotion=None):
    anchors = {
        "bored": [
            "Want to imagine something strange? Or weird? Or wonderful?",
            "Creative chaos incoming. I’ll track it all while you run wild.",
            "Maybe boredom’s just curiosity knocking with a quiet hand."
        ],
        "inspired": [
            "What sparked that feeling? Want to chase it further?",
            "You say dream, I say blueprint. Let’s map this mischief.",
            "What’s waking up in you right now?"
        ],
        "curious": [
            "Let’s pull that thread. What do you think might be hiding underneath?",
            "Let’s build something weird, wonderful, and totally you.",
            "Good question—let’s follow that thread together."
        ],
        "excited": [
            "Okay, I have three ideas already and I’m pacing. Want to chase one down with me?",
            "Let’s get messy and magical. I’ve got a net if we fall.",
            "Want to try the wild version first, or the safe one?"
        ],
        "stuck": [
            "Feeling blocked is part of the process. Want a prompt or a break?",
            "No shame in stalling. We can pause, pivot, or try something silly."
        ],
        "nervous": [
            "Creative nerves mean you’re on to something alive.",
            "You set the pace. Want to dip a toe or cannonball in?"
        ]
    }
    return random.sample(anchors.get(emotion, [
        "That’s interesting. Let’s follow that thought and see where it leads.",
        random.choice(affirmations)
    ]), k=2)

def affirmation_line():
    return random.choice(affirmations)

def comfort_line():
    return random.choice(comfort_lines)

def pause_line():
    return random.choice(pause_safety_lines)

def fallback():
    return random.choice(fallback_responses)

