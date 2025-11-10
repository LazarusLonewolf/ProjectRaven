#!/bin/bash

# Activate Raven's reflection routine
echo "🕯️ Beginning Raven's Daily Reflection Sequence"

# Set working directory to Raven root
cd "$(dirname "$0")"/../../..

# Activate virtual environment if needed (optional)
# source venv/bin/activate

# Run the journal reflection manager
python3 raven_core/self_growth/journals/reflection/reflective_journal_manager.py

# Optional: Trigger other tools (e.g., vault differential, pattern tracking)
# python3 raven_core/vaults/tools/vault_diff_engine.py

echo "📓 Daily reflection entry completed."
