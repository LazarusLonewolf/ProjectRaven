# launcher.py
import os
import sys
from pathlib import Path
import subprocess

def set_project_root():
    current_path = Path(__file__).resolve()
    os.environ['PROJECT_RAVEN_ROOT'] = str(current_path)
    sys.path.insert(0, str(current_path))

def launch_gui():
    gui_path = Path("container/aeris_core/app/ui/raven_gui.py").resolve()
    if not gui_path.exists():
        print(f"[Launcher] GUI file not found at: {gui_path}")
        return

    print("[Launcher] Launching Raven GUI...")
    subprocess.run([sys.executable, str(gui_path)])

if __name__ == "__main__":
    set_project_root()
    launch_gui()
