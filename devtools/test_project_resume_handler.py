# test_project_resume_handler.py

import sys
import os
import json

devtools_path = os.path.join(os.path.dirname(__file__))
if devtools_path not in sys.path:
    sys.path.append(devtools_path)

import project_resume_handler

def test_resume_structure():
    print("[TEST] Running Project Resume Handler Test...")

    resume_data = project_resume_handler.build_project_resume()
    if not isinstance(resume_data, dict):
        print("[FAIL] Resume data is not a dictionary.")
        return

    print("[PASS] Resume structure is valid.")

    json_output = project_resume_handler.write_resume_json(resume_data)
    if not os.path.exists(json_output):
        print(f"[FAIL] JSON file not found at expected location: {json_output}")
        return

    print(f"[PASS] JSON resume file created successfully at: {json_output}")

if __name__ == "__main__":
    test_resume_structure()