# raven_gui.py

import os, sys, importlib.util, tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

HERE = Path(__file__).resolve()

def _find_project_root():
    """
    Walk upward until we see raven_path_initializer.py or a 'raven_core' dir.
    Falls back to 4-levels-up (expected .../Raven) if not found.
    """
    for p in HERE.parents:
        if (p / "raven_path_initializer.py").exists():
            return p
        if (p / "raven_core").is_dir():
            return p
    # heuristic: Raven/ is usually 4 levels up from ui/
    return HERE.parents[3] if len(HERE.parents) >= 4 else HERE.parent

PROJECT_ROOT = _find_project_root()
os.environ.setdefault("RAVEN_ROOT", str(PROJECT_ROOT))

# ensure root is importable before we try to import raven_path_initializer
root_str = str(PROJECT_ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

# import raven_path_initializer with a safe fallback to file load
try:
    from raven_path_initializer import set_project_root, initialize_paths
except ModuleNotFoundError:
    init_path = PROJECT_ROOT / "raven_path_initializer.py"
    if not init_path.exists():
        raise RuntimeError(f"[bootstrap] raven_path_initializer.py not found under {PROJECT_ROOT}")
    spec = importlib.util.spec_from_file_location("raven_path_initializer", str(init_path))
    _mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_mod)
    set_project_root = getattr(_mod, "set_project_root")
    initialize_paths = getattr(_mod, "initialize_paths")

# now call the ushers
set_project_root()
initialize_paths()

# --- Canonical directories ---
UI_DIR        = Path(__file__).resolve().parent                    # .../container/aeris_core/app/ui
APP_DIR       = UI_DIR.parent                                      # .../container/aeris_core/app
AERIS_DIR     = APP_DIR.parent                                     # .../container/aeris_core
CONTAINER_DIR = AERIS_DIR.parent                                   # .../container
PROJECT_ROOT  = CONTAINER_DIR.parent                               # .../Raven

os.environ.setdefault("RAVEN_ROOT", str(PROJECT_ROOT))

# --- Path bootstrap ---
paths_to_add = [
    str(APP_DIR),
    str(APP_DIR / "utilities"),
    str(APP_DIR / "raven_core"),
    str(APP_DIR / "raven_core" / "self_growth" / "memory"),
    str(PROJECT_ROOT / "tools"),
    str(PROJECT_ROOT / "tools" / "sandbox"),
    str(PROJECT_ROOT / "tools" / "sandbox" / "parsing"),
]
for p in paths_to_add:
    if p not in sys.path:
        sys.path.insert(0, p)

# Bus + events
from raven_bus import register_event_listener as bus_register_event_listener, dispatch as bus_dispatch

# --- Initialize paths (optional) ---
try:
    from raven_path_initializer import initialize_paths
    initialize_paths()
except Exception as e:
    print(f"[paths] initialize_paths skipped: {e}")

# --- Utilities: get_full_path ---
UTILITIES_PATH = APP_DIR / "utilities" / "path_refactor.py"
utilities_spec = importlib.util.spec_from_file_location("utilities.path_refactor", str(UTILITIES_PATH))
utilities_module = importlib.util.module_from_spec(utilities_spec)
utilities_spec.loader.exec_module(utilities_module)
get_full_path = getattr(utilities_module, "get_full_path", None)
if not callable(get_full_path):
    raise RuntimeError("[path_refactor] get_full_path not found")

# --- Optional: optimization (robust fallback) ---
try:
    from optimization.optimization_core import Optimizer
except Exception:
    from importlib.util import spec_from_file_location, module_from_spec
    candidates = [
        PROJECT_ROOT / "tools" / "optimization"  / "optimization_core.py",
        PROJECT_ROOT / "tools" / "Optimmization" / "optimization_core.py",
        PROJECT_ROOT / "tools" / "optimization"  / "core.py",
        PROJECT_ROOT / "tools" / "Optimmization" / "core.py",
    ]
    mod = None
    for oc_path in candidates:
        if oc_path.exists():
            spec = spec_from_file_location("optimization_core", str(oc_path))
            mod  = module_from_spec(spec)
            spec.loader.exec_module(mod)
            break
    Optimizer = getattr(mod, "Optimizer", getattr(mod, "optimizer", None)) if mod else None

# --- Dynamic sandbox_core loader -> process_file ---
def load_sandbox_process_file():
    root_sandbox = PROJECT_ROOT / "tools" / "sandbox" / "sandbox_core.py"
    sandbox_path = str(root_sandbox) if root_sandbox.exists() else get_full_path('tools/sandbox/sandbox_core.py')
    spec = importlib.util.spec_from_file_location("sandbox_core", sandbox_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.process_file

process_file = load_sandbox_process_file()

# --- Optional mode router ---
try:
    mr_path = APP_DIR / "mode_router.py"
    spec = importlib.util.spec_from_file_location("mode_router", str(mr_path))
    mode_router = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mode_router)
    load_mode_instance = mode_router.load_mode_instance
except Exception:
    load_mode_instance = lambda *_args, **_kw: None

# --- RavenMail watcher ---
try:
    from utilities.ravenmail_watcher import RavenMailWatcher
except Exception:
    rmw_path = APP_DIR / "utilities" / "ravenmail_watcher.py"
    spec = importlib.util.spec_from_file_location("ravenmail_watcher", str(rmw_path))
    rmw  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rmw)
    RavenMailWatcher = getattr(rmw, "RavenMailWatcher")

# --- Core import ---
from raven_core.raven_core_controller import RavenCoreController

class RavenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Raven AI")
        self.mode_instance = None
        self.last_sandbox_result = None
        self.core = RavenCoreController()

        # Events from bus -> GUI
        bus_register_event_listener("ravenmail_file", self.handle_ravenmail_file)

        # RavenMail watcher toggle
        self.watcher = RavenMailWatcher()
        self.watching = tk.BooleanVar(value=False)

        # Mode selector
        self.mode_names = ['Raven', 'Connor Mode', 'Comfort Mode', 'Muse Mode', 'Shadow Mode']
        self.mode_var = tk.StringVar()
        self.mode_selector = ttk.Combobox(root, textvariable=self.mode_var, state="readonly", values=self.mode_names)
        self.mode_selector.current(0)
        self.mode_selector.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.mode_selector.bind("<<ComboboxSelected>>", self.switch_mode)

        # RavenMail watch toggle
        self.watch_btn = ttk.Checkbutton(root, text="Watch RavenMail",
                                         variable=self.watching, command=self.toggle_watch)
        self.watch_btn.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Output display
        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, width=80)
        self.output_area.grid(row=1, column=0, columnspan=4, padx=10, pady=10)
        self.output_area.config(state='disabled')

        # Input field + send
        self.input_entry = tk.Entry(root, width=70)
        self.input_entry.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.input_entry.bind("<Return>", self.handle_input_event)

        self.send_button = tk.Button(root, text="Send", command=self.handle_input)
        self.send_button.grid(row=2, column=1, padx=5, pady=10, sticky="w")

        # Sandbox button
        self.sandbox_button = tk.Button(root, text="Sandbox",
                                        command=lambda: self.handle_input(sandbox_trigger=True))
        self.sandbox_button.grid(row=2, column=2, padx=5, pady=10, sticky="e")

        # Folder buttons
        self.open_out_btn = tk.Button(root, text="Open Sandbox Folder", command=self.open_out_folder)
        self.open_out_btn.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.open_vaults_btn = tk.Button(root, text="Open Vaults Inbox", command=self.open_vaults_folder)
        self.open_vaults_btn.grid(row=3, column=2, padx=5, pady=5, sticky="w")

        self.send_vaults_btn = tk.Button(root, text="Send Last to Vaults", command=self.send_last_to_vaults)
        self.send_vaults_btn.grid(row=3, column=3, padx=5, pady=5, sticky="w")

    # --- UI helpers ---
    def append_output(self, text: str):
        self.output_area.config(state='normal')
        self.output_area.insert('end', (text or '') + '\n')
        self.output_area.see('end')
        self.output_area.config(state='disabled')

    def display_output(self, text):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, (text or "") + "\n")
        self.output_area.config(state='disabled')
        self.output_area.yview(tk.END)

    def show_modal(self, title, message, options=None):
        return messagebox.askquestion(title, message)  # 'yes' or 'no'
        
    def _load_sandbox_core_module():
        spec = importlib.util.spec_from_file_location("sandbox_core", get_full_path('tools/sandbox/sandbox_core.py'))
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    # --- RavenMail watcher control ---
    def toggle_watch(self):
        if self.watching.get():
            try:
                self.watcher.start()
                self.update_status(f"Watching RavenMail: {Path(PROJECT_ROOT) / 'RavenMail'}")
            except Exception as e:
                self.update_status(f"Watcher error: {e}")
        else:
            try:
                self.watcher.stop()
            finally:
                self.update_status("RavenMail watcher stopped.")

    # --- Events from bus ---
    def handle_ravenmail_file(self, file_path: str):
        fname = os.path.basename(file_path)
        choice = self.show_modal(
            title="RavenMail Received",
            message=f"File '{fname}' received. Send to Sandbox now?",
            options=["Yes", "No"]
        )
        if str(choice).lower() == "yes":
            try:
                result = process_file(file_path)
                result["source_file"] = file_path
                self.last_sandbox_result = result
                self.display_output(f"[RavenMail] {fname} → processed.")
                self._show_sandbox_result(result)
            except Exception as e:
                self.display_output(f"[RavenMail] Error processing '{fname}': {e}")
        else:
            self.update_status("File received but not sent to Sandbox.")

    def _show_sandbox_result(self, result: dict):
        if not isinstance(result, dict):
            self.display_output(str(result)); return
        saved_to = result.get("saved_to")
        preview  = result.get("preview")
        kind     = result.get("type", "?")
        ok       = result.get("ok", True) and "error" not in result

        if ok:
            self.display_output(f"[Sandbox] Type={kind} Saved={saved_to or '(none)'}")
            if preview:
                self.display_output(f"[Preview] {preview}")
            elif saved_to and os.path.exists(saved_to):
                try:
                    txt = Path(saved_to).read_text(encoding="utf-8", errors="ignore")
                    self.display_output(f"[Preview] {txt[:240]}{'…' if len(txt)>240 else ''}")
                except Exception as e:
                    self.display_output(f"[Preview] unable to read saved file: {e}")
        else:
            self.display_output(f"[Sandbox] ERROR: {result.get('error', 'unknown error')}")

    def update_status(self, message):
        self.display_output(f"[STATUS] {message}")

    # --- Mode switching / conversation ---
    def switch_mode(self, _event=None):
        selected = (self.mode_var.get() or "").strip()

        # Map label -> engine key
        label_to_key = {
            "Raven":        "raven",
            "Connor Mode":  "connor",
            "Comfort Mode": "comfort",
            "Muse Mode":    "muse",
            "Shadow Mode":  "shadow",
        }
        key = label_to_key.get(selected)
        if not key:
            self.display_output(f"Mode '{selected}' not recognized.")
            return

        # Ask Core to switch (single call)
        try:
            reply = self.core.respond_to(f"/mode {key}")
        except Exception as e:
            reply = f"[core error] {e}"

        # Show result
        self.display_output(f"Raven: {reply}")

        # Keep dropdown in sync with whatever Core accepted
        if isinstance(reply, str) and reply.startswith("[Raven] Mode set to "):
            # success path: already pointing at user's selection
            return

        # If Core corrected/denied, read target from text and update combobox
        try:
            target = reply.split("set to ", 1)[1].strip(".").strip().lower()
        except Exception:
            target = ""

        key_to_label = {
            "raven": "Raven",
            "connor": "Connor Mode",
            "comfort": "Comfort Mode",
            "muse": "Muse Mode",
            "shadow": "Shadow Mode",
            "shadowlantern": "Shadow Mode",  # legacy alias if Core returns it
            "core": "Raven",
        }
        if target in key_to_label:
            self.mode_var.set(key_to_label[target])

    # --- Enter-key wrapper ---
    def handle_input_event(self, _evt):
        self.handle_input(sandbox_trigger=False)
        return "break"

        # --- Input handler ---
    def handle_input(self, sandbox_trigger: bool=False):
        text = self.input_entry.get().strip()
        if not text and not sandbox_trigger:
            return

        # 1) Sandbox quick path
        if sandbox_trigger:
            try:
                result = process_file(text) if text else "[sandbox] Provide a file path in the input."
                self.append_output(str(result))
            except Exception as e:
                self.append_output(f"[sandbox error] {e}")
            return

        # 2) Core conversation path (prefer controller; fallback to bus)
        try:
            reply = self.core.respond_to(text)
        except Exception:
            try:
                reply = bus_dispatch(text)
            except Exception as e:
                reply = f"[core error] {e}"

        # normalize + ensure non-empty
        reply = reply if isinstance(reply, str) else str(reply)
        if not reply:
            reply = "[Raven] (no text)"


        # Normalize reply to a non-empty string
        if not isinstance(reply, str):
            reply = str(reply)
        if not reply:
            reply = "[Raven] (no text)"

        # UI output
        self.append_output(f"You: {text}")
        self.append_output(f"Raven: {reply}")
        self.input_entry.delete(0, 'end')

        # Reflect mode in dropdown if a mode-set message came back
        if reply.startswith("[Raven] Mode set to "):
            target = reply.split("set to ", 1)[1].strip(".").strip().lower()
            label_map = {
                "raven":"Raven", "connor":"Connor Mode",
                "comfort":"Comfort Mode", "muse":"Muse Mode",
                "shadow":"Shadow Mode", "shadowlantern":"Shadow Mode",
                "core":"Raven"
            }
            lbl = label_map.get(target)
            if lbl:
                # Only mirror the mode; do NOT call switch_mode() again
                self.mode_var.set(lbl)

     # --- Buttons: folders / vaults ---
    def open_out_folder(self):
        try:
            out_dir = Path(os.environ.get("RAVEN_ROOT", PROJECT_ROOT)) / "out" / "sandbox"
            out_dir.mkdir(parents=True, exist_ok=True)
            os.startfile(str(out_dir))
        except Exception as e:
            self.display_output(f"[STATUS] Could not open sandbox folder: {e}")

    def open_vaults_folder(self):
        try:
            root = Path(os.environ.get("RAVEN_ROOT", PROJECT_ROOT))
            vaults_dir = root / "vaults" / "inbox"
            vaults_dir.mkdir(parents=True, exist_ok=True)
            os.startfile(str(vaults_dir))
        except Exception as e:
            self.display_output(f"[STATUS] Could not open vaults inbox: {e}")

    def send_last_to_vaults(self):
        """
        Move the last sandbox artifact into vaults/inbox using tools.sandbox.sandbox_core.send_to_vault
        """
        try:
            if not self.last_sandbox_result or not isinstance(self.last_sandbox_result, dict):
                self.display_output("[Vaults] Nothing to send. Process a file first.")
                return

            saved = self.last_sandbox_result.get("saved_to")
            if not saved:
                self.display_output("[Vaults] Last result had no saved artifact.")
                return

            # Load sandbox_core and call send_to_vault (singular)
            spec = importlib.util.spec_from_file_location("sandbox_core", get_full_path('tools/sandbox/sandbox_core.py'))
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            send_to_vault = getattr(mod, "send_to_vault", None)
            if not callable(send_to_vault):
                self.display_output("[Vaults] ERROR: sandbox_core.send_to_vault not found.")
                return
                
            res = send_to_vault(
                saved_path=saved,
                source_file=self.last_sandbox_result.get("source_file", ""),
                meta={
                    "type":  self.last_sandbox_result.get("type"),
                    "chars": self.last_sandbox_result.get("chars"),
                },
            )
            
            if isinstance(res, dict) and res.get("ok"):
                self.display_output(f"[Vaults] Moved to inbox: {res.get('artifact')}")
            else:
                err = (res or {}).get("error") if isinstance(res, dict) else "Unknown error"
                self.display_output(f"[Vaults] ERROR: {err}")

        except Exception as e:
            self.display_output(f"[Vaults] ERROR: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RavenGUI(root)
    root.mainloop()
