# numerology_engine.py – Symbolic Insight Engine (Numerology Variant)
# Calculates life path numbers and provides basic interpretations

def calculate_life_path_number(birthdate_str):
    # Format: MM-DD-YYYY
    digits = [int(ch) for ch in birthdate_str if ch.isdigit()]
    total = sum(digits)

    # Reduce to life path number (except master numbers)
    while total > 9 and total not in [11, 22, 33]:
        total = sum([int(d) for d in str(total)])

    return total

def interpret_life_path(number):
    meanings = {
        1: "Leadership, independence, and ambition. You’re here to pioneer new paths.",
        2: "Sensitivity, diplomacy, and cooperation. Harmony matters deeply to you.",
        3: "Creativity, joy, and expression. You’re here to inspire and uplift.",
        4: "Stability, discipline, and responsibility. You build lasting structures.",
        5: "Freedom, change, and adventure. Life teaches you through movement.",
        6: "Service, compassion, and harmony in the home. You’re a nurturer and guide.",
        7: "Spiritual insight, analysis, and introspection. Wisdom is your journey.",
        8: "Power, success, and material mastery. You’re here to shape outcomes.",
        9: "Compassion, humanitarianism, and letting go. You bring closure and depth.",
        11: "Spiritual intuition, illumination, and vision. You’re a messenger of light.",
        22: "Master builder, grounded dreams into lasting reality.",
        33: "The master teacher — unconditional love, healing, and inspired truth."
    }
    return meanings.get(number, "Unknown life path number.")

