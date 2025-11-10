# test_emotional_tagging.py
import sys
import os

# Explicitly add the memory folder to the path
sys.path.append("/app/memory")

from emotional_tagging import analyze

def run_test():
    samples = [
        "I'm so happy and excited for tomorrow!",
        "I don't know how I feel — it's just weird.",
        "I'm distracted and can't concentrate at all.",
        "Honestly, I feel everything at once and nothing feels right.",
        "I'm curious about how this works.",
        "My brain won't stop and I can't sit still.",
        "Meh. I'm kind of bored and restless.",
        "I'm nervous and afraid it won’t work out."
    ]

    for idx, entry in enumerate(samples, start=1):
        emotion = analyze(entry)
        print(f"[TEST] Sample {idx}: {entry}")
        print(f"[RESULT] Detected Emotion: {emotion}\n")

if __name__ == "__main__":
    run_test()
