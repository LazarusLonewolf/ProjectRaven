# tarot_engine.py – Symbolic Insight Engine (Tarot Variant)
# Loads card data from CSV and simulates randomized card draws with orientation

import os
import csv
import random

def load_tarot_data():
    file_path = os.path.join(os.path.dirname(__file__), 'tarot_card_meanings.csv')
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

tarot_deck = load_tarot_data()

def draw_cards(num_cards=1):
    drawn = []
    used_cards = set()

    while len(drawn) < num_cards:
        candidate = random.choice(tarot_deck)
        card_name = candidate["card"]

        if card_name not in used_cards:
            used_cards.add(card_name)
            drawn.append({
                "card": card_name,
                "orientation": candidate["orientation"],
                "meaning": candidate["meaning"]
            })

    return drawn
    
def draw_spread(count=3):
    return draw_cards(count)

def format_reading(spread):
    output = []
    for i, card in enumerate(spread, 1):
        direction = "(Reversed)" if card["orientation"].lower() == "reversed" else "(Upright)"
        entry = f"{i}. {card['card']} {direction}: {card['meaning']}"
        output.append(entry)
    return "\n".join(output)

if __name__ == "__main__":
    print("=== Tarot Reading ===")
    sample_spread = draw_cards(3)
    print(format_reading(sample_spread))


