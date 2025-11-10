# test_garden_core.py
import sys
import os
sys.path.append("/app")

from memory.garden.garden_core import RavenGarden

def run_test():
    print("[TEST] Creating Raven's symbolic garden...")
    garden = RavenGarden()

    print("[TEST] Planting anchors...")
    garden.plant("Hope", "emotion")
    garden.plant("Casey", "person")
    garden.plant("First Memory", "milestone")

    print("[TEST] Anchoring memories...")
    garden.anchor_memory("Hope", "intro_doc")
    garden.anchor_memory("Casey", "user_casey")
    garden.anchor_memory("First Memory", "journal_001")

    print("[TEST] Garden state:")
    anchors = garden.describe()
    for anchor in anchors:
        print(f" - {anchor}")

if __name__ == "__main__":
    run_test()
