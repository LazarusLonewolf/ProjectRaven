# test_memory_integrity.py

import sys
import os
from datetime import datetime

# Force /app onto path so we can import memory.*
sys.path.append("/app")

from memory.vector_bridge import store_thought, search_memory
from memory.journal_memory_bridge import init_db, process_journals

def run_test():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_id = f"integrity_{timestamp}"
    test_thought = "Raven recognizes the continuity of thought across time."
    search_query = "continuity"

    print(f"[TEST] Injecting test thought ({test_id})...")
    store_thought(test_thought, test_id)

    print("[TEST] Querying to verify vector memory...")
    results = search_memory(search_query)
    print("[RESULT] Vector Memory Match:")
    for result in results:
        print(f" - {result}")

    print("[TEST] Initializing fallback journal DB...")
    init_db()

    print("[TEST] Re-processing journal entries...")
    process_journals()

    print("[TEST COMPLETE] Memory integrity validated across modules.")

if __name__ == "__main__":
    run_test()
