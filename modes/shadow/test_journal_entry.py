# test_journal_entry.py
# Independent test for Shadow Mode journaling

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'modes', 'shadow')))

import journaling

# Simulated user profile and input
test_user = {"name": "TestUser"}
test_input = "This is a test journal entry to verify logging."

# Run journaling test
confirmation = journaling.create_entry(test_input, test_user)
print(confirmation)

# Optionally display last few entries to confirm
recent = journaling.get_recent_entries()
print("\nRecent Entries:")
for line in recent:
    print(line.strip())


