# test_intent_mapper.py

import sys
sys.path.append("/app")

from analysis.intent_mapper import map_intents

def run_test():
    sample_input = """
    I want to improve my sleep and reduce my stress levels.
    My goal is to reconnect with others and feel more grounded day to day.
    I'm trying to build a better routine but it's been difficult lately.
    """

    print("[TEST] Running Intent Mapping and Gap Analysis...\n")
    result = map_intents(sample_input)

    print("[RESULT] Key Phrases Detected:")
    for phrase in result["key_phrases"]:
        print(f" - {phrase}")

    print("\n[RESULT] Goal Gap Map:")
    for goal, found in result["gap_analysis"].items():
        status = "FOUND" if found else "MISSING"
        print(f" - {goal}: {status}")

if __name__ == "__main__":
    run_test()

