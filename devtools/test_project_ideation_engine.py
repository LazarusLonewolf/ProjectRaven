# test_project_ideation_engine.py

from devtools import project_ideation_engine

def run_ideation_test():
    print("Welcome to Raven's Game Ideation Assistant!")
    print("Please answer the following prompts to help define your game concept.\n")

    responses = project_ideation_engine.start_ideation()
    
    print("\n--- Ideation Summary ---")
    for key, value in responses.items():
        print(f"{key.replace('_', ' ').capitalize()}: {value}")

if __name__ == "__main__":
    run_ideation_test()
