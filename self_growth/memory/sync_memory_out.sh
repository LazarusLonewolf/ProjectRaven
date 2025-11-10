#!/bin/bash

# Define the persistent target directory on the host system
HOST_MEMORY_DIR="/app/memory"
TARGET_SYNC_DIR="/app/memory"  # We’ll map this in the volume

echo "[SYNC] Copying memory DB files to /app/memory/db_sync/..."
mkdir -p /app/memory/db_sync/
cp /app/memory/*.db /app/memory/db_sync/
echo "[SYNC] Sync complete."
