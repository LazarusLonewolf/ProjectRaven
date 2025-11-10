# tools/sandbox/sandbox_core.py
import os, sys, json, traceback
from datetime import datetime
from pathlib import Path

# Always initialize Raven paths first
from raven_path_initializer import (
    BASE_RAVEN_PATH,
    APP_PATH,
    RAVEN_CORE_PATH,
    get_full_path,
    try_import,
)

# --- import tools via try_import (safe) ---
# NOTE: do NOT import tools.sandbox.sandbox_core here (that would self-import this file)
parser = try_import("tools.sandbox.parsing.document_parser", alias="parser")
ocr     = try_import("tools.sandbox.parsing.ocr_reader", alias="ocr")

# Lazy + safe accessor to avoid circular import at import time
try:
    from raven_core.raven_app_initializer import get_tool  # prefer namespaced path
except Exception:
    try:
        from raven_app_initializer import get_tool
    except Exception:
        def get_tool(*args, **kwargs):
            return None  # degrade gracefully if initializer isn't ready

# --- Output & routing helpers ---
RAVEN_ROOT = Path(os.environ.get("RAVEN_ROOT", BASE_RAVEN_PATH))
OUT_DIR    = RAVEN_ROOT / "out" / "sandbox"
VAULT_DIR  = RAVEN_ROOT / "vaults" / "inbox"   # <- plural to match GUI
VAULT_IDX  = RAVEN_ROOT / "vaults" / "index.json"
OUT_DIR.mkdir(parents=True, exist_ok=True)
VAULT_DIR.mkdir(parents=True, exist_ok=True)

DOCUMENT_EXTS = {".txt", ".pdf", ".docx", ".md", ".rtf", ".log"}
IMAGE_EXTS    = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

def _save_text(src: Path, text: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{src.stem}.extracted.txt"
    out.write_text(text or "", encoding="utf-8", errors="ignore")
    return out

def _summarize(text: str, limit: int = 240) -> str:
    t = (text or "").replace("\r", " ").replace("\n", " ").strip()
    return t[:limit] + ("…" if len(t) > limit else "")

def _get_parser():
    # prefer your aliased module from try_import; fall back to get_tool("document_parser")
    if parser:
        return parser
    return get_tool("document_parser")

def _get_ocr():
    # prefer your aliased module from try_import; fall back to get_tool("ocr_reader")
    if ocr:
        return ocr
    return get_tool("ocr_reader")

# --- Logging and history paths ---
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "sandbox_history.json")

# --- Logging helpers ---
def log_boot(status):
    """Appends a boot or status message to the sandbox log file."""
    with open(get_full_path("sandbox_boot_log.txt"), "a", encoding="utf-8") as log:
        log.write(f"[{datetime.utcnow()}] {status}\n")

def log_error(context, error):
    """Logs a detailed error with context and traceback."""
    with open(get_full_path("sandbox_error_log.txt"), "a", encoding="utf-8") as log:
        log.write(f"[{datetime.utcnow()}] ERROR in {context}: {error}\n")
        log.write(traceback.format_exc() + "\n")

# --- History helpers (kept as-is, using local JSON file) ---
def append_history(entry):
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = []
        history.append(entry)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log_error("append_history", e)

def get_recent_history(limit=10):
    try:
        if not os.path.exists(HISTORY_FILE):
            return []
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
        return history[-limit:]
    except Exception as e:
        log_error("get_recent_history", e)
        return []

def summarize_history(limit=10):
    try:
        entries = get_recent_history(limit)
        if not entries:
            return "No recent sandbox activity found."
        lines = []
        for e in entries:
            ts = e.get("timestamp", "Unknown time")
            file_name = os.path.basename(e.get("file", "Unknown file"))
            method = e.get("method", "Unknown method")
            status = e.get("status", "unknown").upper()
            if status == "ERROR":
                detail = (e.get("details") or {}).get("error", "Unknown error")
                lines.append(f"[{ts}] {file_name} via {method} → ERROR: {detail}")
            else:
                lines.append(f"[{ts}] {file_name} via {method} → SUCCESS")
        return "\n".join(lines)
    except Exception as e:
        log_error("summarize_history", e)
        return "Error summarizing history."

# keep your no-op, used when data isn't a filepath
def send_to_sandbox(data):
    print("[DEBUG] send_to_sandbox called with:", data)
    return {"status": "sandbox_disabled", "data": data}

def process_file(filepath):
    """Processes a file via OCR or document parser, saves extracted text, logs to history."""
    p = Path(filepath)
    if not p.exists():
        msg = f"File not found: {filepath}"
        log_error("process_file", msg)
        append_history({
            "timestamp": datetime.utcnow().isoformat(),
            "file": str(filepath),
            "ext": p.suffix.lower(),
            "method": "unknown",
            "status": "error",
            "details": {"error": msg}
        })
        return {"ok": False, "error": msg}

    log_boot(f"Processing file: {filepath}")
    ext = p.suffix.lower()
    result = {}
    text = ""

    try:
        # --- Route by type ---
        if ext in IMAGE_EXTS:
            log_boot("Using OCR pipeline for image")
            ocr_mod = _get_ocr()
            if not ocr_mod:
                raise RuntimeError("no OCR implementation available")

            # Support both signatures: ocr_image(path) -> {"ok":bool,"text":...} or extract_text_from_image(path)->str
            if hasattr(ocr_mod, "ocr_image"):
                res = ocr_mod.ocr_image(str(p))
                if not (isinstance(res, dict) and res.get("ok")):
                    raise RuntimeError((res or {}).get("error") or "OCR failed")
                text = res.get("text", "") or ""
            elif hasattr(ocr_mod, "extract_text_from_image"):
                text = ocr_mod.extract_text_from_image(str(p)) or ""
                if not text.strip():
                    raise RuntimeError("empty OCR result")
            else:
                raise RuntimeError("no OCR implementation available")

            saved = _save_text(p, text)
            result = {
                "ok": True,
                "type": "image",
                "saved_to": str(saved),
                "chars": len(text),
                "preview": _summarize(text),
            }

        elif ext in DOCUMENT_EXTS:
            log_boot("Using document parser pipeline")
            parser_mod = _get_parser()
            if not parser_mod:
                raise RuntimeError("no document parser available")

            # Support both: parse_document(path)->{"ok":..., "text":...} or extract_text_from_file(path)->str
            if hasattr(parser_mod, "parse_document"):
                res = parser_mod.parse_document(str(p))
                if not (isinstance(res, dict) and res.get("ok")):
                    raise RuntimeError((res or {}).get("error") or "parse failed")
                text = res.get("text", "") or ""
            elif hasattr(parser_mod, "extract_text_from_file"):
                text = parser_mod.extract_text_from_file(str(p)) or ""
            else:
                raise RuntimeError("no document parser available")

            # Optional secondary parse to structured
            structured = {}
            if hasattr(parser_mod, "parse_text"):
                try:
                    structured = parser_mod.parse_text(text) or {}
                except Exception as e:
                    log_error("Text Parsing", e)

            saved = _save_text(p, text)
            result = {
                "ok": True,
                "type": "document",
                "saved_to": str(saved),
                "chars": len(text),
                "preview": _summarize(text),
                "structured": structured or None,
            }

        else:
            raise ValueError(f"Unsupported file type: {ext}")

        append_history({
            "timestamp": datetime.utcnow().isoformat(),
            "file": str(p),
            "ext": ext,
            "method": "OCR" if ext in IMAGE_EXTS else "Parser",
            "status": "success",
            "details": {"saved_to": result.get("saved_to"), "chars": result.get("chars")},
        })
        return result

    except Exception as e:
        log_error("process_file", e)
        append_history({
            "timestamp": datetime.utcnow().isoformat(),
            "file": str(p),
            "ext": ext,
            "method": "OCR" if ext in IMAGE_EXTS else "Parser",
            "status": "error",
            "details": {"error": str(e)},
        })
        return {"ok": False, "error": str(e)}

def get_sandbox_state():
    return {"status": "sandbox ready"}

def reset_sandbox():
    log_boot("Sandbox reset triggered.")
    return True

def sandbox_message():
    return "Sandbox environment initialized and operational."

def run_sandbox(data):
    # if a file path, process; otherwise keep your current no-op behavior
    if isinstance(data, str) and os.path.isfile(data):
        return process_file(data)
    return send_to_sandbox(data)

def send_to_vault(saved_path: str, *, source_file: str, meta: dict | None = None) -> dict:
    """
    Move saved text artifact into vault/inbox and append a tiny index record.
    """
    try:
        src = Path(saved_path)
        if not src.exists():
            return {"ok": False, "error": f"saved artifact missing: {src}"}

        dest = VAULT_DIR / src.name
        src.replace(dest)

        # minimal index append
        rec = {
            "ts": datetime.utcnow().isoformat(),
            "artifact": str(dest),
            "source_file": source_file,
            "meta": meta or {}
        }
        idx = []
        if VAULT_IDX.exists():
            try:
                idx = json.loads(VAULT_IDX.read_text(encoding="utf-8"))
                if not isinstance(idx, list): idx = []
            except Exception:
                idx = []
        idx.append(rec)
        VAULT_IDX.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")

        return {"ok": True, "artifact": str(dest)}
    except Exception as e:
        log_error("send_to_vault", e)
        return {"ok": False, "error": str(e)}
