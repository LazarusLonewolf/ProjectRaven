# test_herbal_lookup.py
# Quick test for herbal_naturopathic_lookup.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utilities import herbal_naturopathic_lookup as hnl

def run_test():
    test_queries = [
        "stress",
        "insomnia",
        "focus",
        "headache",
        "calm",
        "energy"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        results = hnl.lookup_remedy(query)
        if results:
            for item in results:
                print(f" - {item['Name']} ({item['Type']}): {item['Description']}")
        else:
            print("No match found.")

if __name__ == "__main__":
    run_test()
