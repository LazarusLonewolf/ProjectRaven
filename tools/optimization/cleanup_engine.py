# cleanup_engine.py

import os
import tempfile
import shutil

def get_temp_files_summary():
    temp_dir = tempfile.gettempdir()
    total_files = 0
    total_size = 0
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            try:
                path = os.path.join(root, f)
                total_files += 1
                total_size += os.path.getsize(path)
            except:
                continue
    return {"files": total_files, "approx_size_mb": total_size // (2**20)}

def perform_temp_cleanup():
    temp_dir = tempfile.gettempdir()
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            try:
                os.remove(os.path.join(root, f))
            except:
                continue
