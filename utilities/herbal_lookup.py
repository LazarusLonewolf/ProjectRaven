# herbal_lookup.py – Updated Matching Logic with Token Filtering

import os
import csv

def load_remedy_data():
    file_path = os.path.join(os.path.dirname(__file__), 'herbal_naturopathic_lookup.csv')
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

remedy_data = load_remedy_data()

def query_remedy(user_input):
    query = user_input.lower()
    direct_matches = []
    fallback_matches = []

    for entry in remedy_data:
        target = entry["Target"].lower()
        use = entry["Use"].lower()

        if "anxiety" in target:
            direct_matches.append(f"{entry['Name']} ({entry['Type']}): {entry['Use']}")
        elif "anxiety" in use:
            fallback_matches.append(f"{entry['Name']} ({entry['Type']}): {entry['Use']}")
        elif any(word in target or word in use for word in query.split()):
            fallback_matches.append(f"{entry['Name']} ({entry['Type']}): {entry['Use']}")

    results = direct_matches or fallback_matches

    if not results:
        return "No matching herbal remedies found, but I’m here if you’d like to describe more."

    return "\n".join(results[:3])
