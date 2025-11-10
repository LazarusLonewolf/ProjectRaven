# test_memory_persistence.py

import sys
import os
from datetime import datetime

# Extend sys.path to ensure memory module visibility
sys.path.append("/app")

from memory.vector_bridge import store_thought, search_memory
from memory.journal_memory_bridge import process_journals, init_db

def run_test():
    test_id = f"test_persistence_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    test_text = "Raven recognizes the continuity of thought across time."
    query = "continuity of thought"

    print(f"[TEST] Injecting test thought ({test_id})...")
    store_thought(test_text, test_id)

    print("[TEST] Querying to verify memory persistence...")
    results = search_memory(query)

    print("[RESULT] Match Results:")
    for result in results:
        print(f" - {result}")

    print("[TEST] Initializing fallback journal DB...")
    init_db()

    print("[TEST] Re-processing journal entries...")
    process_journals()

    print("[TEST] Memory test complete.")

if __name__ == "__main__":
    run_test()
