# test_game_creation_tools.py

import os
import sys

# Ensure the devtools directory is in the path
devtools_path = os.path.dirname(__file__)
if devtools_path not in sys.path:
    sys.path.append(devtools_path)

import game_framework

def test_framework_language_detection():
    print("[TEST] Language Detection Check...")
    dummy_files = [
        "main.py", "enemy.py", "level1.py",
        "menu.js", "soundtrack.mp3", "README.md"
    ]
    lang = game_framework.detect_game_language(dummy_files)
    print(f"[RESULT] Detected Language: {lang}")

def test_project_skeleton_creation():
    print("[TEST] Project Skeleton Creation...")
    test_base = "/tmp" if os.name != "nt" else "C:\\temp"
    project_name = "test_game_project"
    project_path = game_framework.create_project_skeleton(test_base, project_name)
    print(f"[RESULT] Project created at: {project_path}")
    print("[SUMMARY]\n" + game_framework.summarize_project(project_path))

if __name__ == "__main__":
    test_framework_language_detection()
    print("-" * 40)
    test_project_skeleton_creation()