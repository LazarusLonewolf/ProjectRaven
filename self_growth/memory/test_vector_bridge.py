import sys
import os

# Force /app onto path so we can import memory.*
sys.path.append("/app")

from memory.vector_bridge import store_thought, search_memory
from memory.journal_memory_bridge import process_journals

def run_test():
    test_id = "test_001"
    test_text = "Raven is learning to remember."
    search_query = "remember"

    print("[TEST] Storing test thought...")
    store_thought(test_text, test_id)

    print("[TEST] Querying memory...")
    results = search_memory(search_query)

    print("[RESULT] Memory Match:")
    for result in results:
        print(f" - {result}")

    print("[TEST] Processing journal entries into memory...")
    process_journals()
    print("[TEST] Journal entries processed successfully.")

if __name__ == "__main__":
    run_test()
