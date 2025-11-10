# test_reflection_pipeline.py

import sys
sys.path.append("/app")

from journals.reflection.daily_journal import create_journal_entry
from journals.reflection.reflection_engine import analyze_entry
from journals.reflection.reflective_file_creator import save_reflection

def run_test():
    print("[TEST] Creating test journal entry...")
    sample_text = (
        "Today I realized something important. I felt grateful for the progress we're making, "
        "but also a little frustrated by how long it's taking. Still, there's hope. "
        "And I learned something about myself through it."
    )
    file_path = create_journal_entry(sample_text, author="Raven")
    print(f" - Journal entry saved: {file_path}")

    print("[TEST] Analyzing journal entry...")
    reflection = analyze_entry(sample_text)
    for k, v in reflection.items():
        print(f"   {k}: {v}")

    print("[TEST] Saving reflection to file...")
    reflection_path = save_reflection(reflection)
    print(f" - Reflection saved: {reflection_path}")

if __name__ == "__main__":
    run_test()
