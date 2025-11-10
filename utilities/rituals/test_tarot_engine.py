# test_tarot_engine.py – Tests for tarot_engine functionality

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utilities.rituals import tarot_engine

def run_tests():
    print("=== Tarot Engine Test ===\n")

    print(">>> Single Card Draw:")
    card = tarot_engine.draw_cards(1)[0]
    print(f"{card['card']} ({card['orientation']}) – {card['meaning']}\n")

    print(">>> Three Card Spread:")
    spread = tarot_engine.draw_cards(3)
    for i, card in enumerate(spread, 1):
        print(f"Card {i}: {card['card']} ({card['orientation']}) – {card['meaning']}")

if __name__ == "__main__":
    run_tests()

