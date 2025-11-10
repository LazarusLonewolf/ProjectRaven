# test_journal_memory_bridge.py

import sys
import os

# Force /app onto path so we can import memory.*
sys.path.append("/app")

from memory.journal_memory_bridge import init_db, process_journals

def run_test():
    print("[TEST] Initializing journal DB...")
    init_db()
    
    print("[TEST] Processing journal entries...")
    process_journals()
    
    print("[TEST] Journal processing complete.")

if __name__ == "__main__":
    run_test()
