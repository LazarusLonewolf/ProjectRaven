# test_numerology_engine.py – Test Script for Numerology Insight Engine

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utilities.rituals import numerology_engine

def run_test():
    print("=== Numerology Engine Test ===\n")

    test_dates = [
        "1981-06-20",  # Example date
        "1995-12-03",  # Random younger profile
        "2000-01-01",  # New millennium birth
        "1977-07-07",  # Repeating digits
        "1988-08-08",  # Master number potential
    ]

    for date in test_dates:
        print(f">>> Testing Birthdate: {date}")
        number = numerology_engine.calculate_life_path_number(date)
        meaning = numerology_engine.interpret_life_path(number)
        print(f"Life Path Number: {number}")
        print(f"Meaning: {meaning}\n")

if __name__ == "__main__":
    run_test()
