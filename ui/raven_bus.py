# raven_bus.py
import os, sys
from pathlib import Path
import importlib.util

RAVEN_ROOT = str(Path(__file__).resolve().parents[4])  # ...\Raven  (was 3)
os.environ.setdefault("RAVEN_ROOT", RAVEN_ROOT)
if RAVEN_ROOT not in sys.path: sys.path.insert(0, RAVEN_ROOT)

tools_root = str(Path(RAVEN_ROOT) / "tools")
if tools_root not in sys.path: sys.path.insert(0, tools_root)
     
raven_root = Path(os.environ["RAVEN_ROOT"])
app_path   = raven_root / "container" / "aeris_core" / "app"
core_path  = raven_root / "raven_core"
root_tools = raven_root / "tools"

# Make packages importable (single pass)
for p in (app_path, app_path/"tools", app_path/"tools"/"sandbox", app_path/"tools"/"sandbox"/"parsing", core_path, root_tools):
    sp = str(p)
    if p.exists() and sp not in sys.path:
        sys.path.insert(0, sp)

# Import sandbox entrypoint (fallback now uses ROOT tools)
try:
    from tools.sandbox.sandbox_core import process_file  # or run_sandbox
except Exception:
    spec = importlib.util.spec_from_file_location(
        "sandbox_core",
        str(Path(tools_root) / "sandbox" / "sandbox_core.py")  # was app_path/... -> now root/tools
    )
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    process_file = getattr(mod, "process_file", getattr(mod, "run_sandbox"))

# Import Raven core text entrypoint
try:
    from raven_core.raven_core_controller import send_to_raven_core
except Exception:
    def send_to_raven_core(text: str):
        raise RuntimeError("send_to_raven_core not found; wire your core text handler here.")

event_listeners = {}

def dispatch(input_text: str):
    if isinstance(input_text, str) and os.path.isfile(input_text):
        return process_file(input_text)
    return send_to_raven_core(input_text)

def register_event_listener(event_type: str, callback):
    event_listeners.setdefault(event_type, []).append(callback)

def trigger_event(event_type: str, *args, **kwargs):
    for cb in event_listeners.get(event_type, []):
        cb(*args, **kwargs)

def on_ravenmail_event(file_path: str):
    trigger_event("ravenmail_file", file_path)

class RavenBus:
    def __init__(self):
        self.subscribers = {}
    def subscribe(self, topic, callback):
        self.subscribers.setdefault(topic, []).append(callback)
    def publish(self, topic, data):
        for cb in self.subscribers.get(topic, []):
            cb(data)

bus = RavenBus()
