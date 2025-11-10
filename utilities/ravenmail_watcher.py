# container/aeris_core/app/utilities/ravenmail_watcher.py

import os, time, shutil, threading
from pathlib import Path

ROOT = Path(os.environ.get("RAVEN_ROOT", Path(__file__).resolve().parents[4]))
WATCH_FOLDER = ROOT / "RavenMail"
DEFAULT_DEST = ROOT / "tools" / "sandbox" / "inbox"
LOGFILE = ROOT / "out" / "logs" / "ravenmail_log.txt"
POLL_INTERVAL = 1.0
MOVE_FILES = False

# --- Bus shim (supports both APIs) ---
try:
    # preferred: event-based API in raven_bus
    from raven_bus import on_ravenmail_event as _emit
except Exception:
    try:
        # fallback: older raven_bus ‘dispatch’ signature(s)
        from raven_bus import dispatch as _bus_dispatch
        def _emit(path: str):
            # try modern signature first, fall back to single-arg variants
            try:
                _bus_dispatch("ravenmail_file", path)
            except TypeError:
                try:
                    _bus_dispatch({"event": "ravenmail_file", "path": path})
                except Exception:
                    print(f"[RavenMail] (bus shim) file ready: {path}")
    except Exception:
        # last resort: just print so we can see it fired
        def _emit(path: str):
            print(f"[RavenMail] (no bus) file ready: {path}")

def _log(msg: str):
    LOGFILE.parent.mkdir(parents=True, exist_ok=True)
    with LOGFILE.open("a", encoding="utf-8") as f:
        f.write(f"[{time.ctime()}] {msg}\n")

def _stable(p: Path) -> bool:
    try:
        s1 = p.stat().st_size; time.sleep(0.2); s2 = p.stat().st_size
        return s1 == s2
    except Exception:
        return False

def route_file(file_path: Path):
    try:
        file_path = Path(file_path)
        if MOVE_FILES:
            DEFAULT_DEST.mkdir(parents=True, exist_ok=True)
            dest = DEFAULT_DEST / file_path.name
            shutil.move(str(file_path), str(dest))
            _log(f"Routed: {file_path.name} → {DEFAULT_DEST}")
            print(f"[RavenMail] Routed: {file_path.name}")
            _emit(str(dest))  # <-- emit moved path
        else:
            _log(f"Detected: {file_path}")
            print(f"[RavenMail] Detected: {file_path.name}")
            _emit(str(file_path))  # <-- unified: always use _emit
    except Exception as e:
        _log(f"ERROR routing {getattr(file_path,'name',file_path)}: {e}")
        print(f"[RavenMail] Error routing: {e}")

class RavenMailWatcher:
    def __init__(self, folder: Path | None = None, poll_interval: float = POLL_INTERVAL):
        self.folder = Path(folder) if folder else WATCH_FOLDER
        self.poll = poll_interval
        self._stop = threading.Event()
        self._thread = None
        self._seen = {}

    def start(self):
        self.folder.mkdir(parents=True, exist_ok=True)
        if self._thread and self._thread.is_alive(): return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        _log(f"Watcher started at {self.folder}")

    def stop(self):
        self._stop.set(); _log("Watcher stopped")

    def _loop(self):
        print("[RavenMail] Mail watcher online.")
        while not self._stop.is_set():
            try:
                for p in self.folder.iterdir():
                    if not p.is_file(): continue
                    stat = p.stat()
                    key = (stat.st_size, int(stat.st_mtime))
                    prev = self._seen.get(p.name)
                    if prev != key and _stable(p):
                        self._seen[p.name] = key
                        route_file(p)
                time.sleep(self.poll)
            except Exception as e:
                _log(f"Loop error: {e}"); time.sleep(self.poll)

# Allow running as a script for quick manual testing
if __name__ == "__main__":
    w = RavenMailWatcher()
    w.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        w.stop()
