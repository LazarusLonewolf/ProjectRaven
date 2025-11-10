# tools/sandbox/sandbox_history_tool.py
from __future__ import annotations
import json, os, time, uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default history file sits next to this module
def _history_file(history_path: Optional[str] = None) -> Path:
    return Path(history_path) if history_path else Path(__file__).resolve().parent / "sandbox_history.json"

def _read_history(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def _atomic_write(path: Path, payload: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{uuid.uuid4().hex}")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def log_event(event_type: str, details: Any = None, *, file_path: Optional[str] = None,
              status: Optional[str] = None, meta: Optional[Dict[str, Any]] = None,
              history_path: Optional[str] = None, max_entries: int = 1000) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        "id": uuid.uuid4().hex,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
        "event": event_type
    }
    if details is not None: entry["details"] = details
    if file_path:            entry["file"] = file_path
    if status:               entry["status"] = status
    if meta:                 entry["meta"] = meta

    path = _history_file(history_path)
    hist = _read_history(path)
    hist.append(entry)
    if max_entries > 0 and len(hist) > max_entries:
        hist = hist[-max_entries:]
    _atomic_write(path, hist)
    return entry

def list_history(limit: Optional[int] = None, *, history_path: Optional[str] = None) -> List[Dict[str, Any]]:
    hist = _read_history(_history_file(history_path))
    return hist[-limit:] if limit and limit > 0 else hist

# Optional helper that returns a human-friendly summary without importing sandbox_core
def summarize_history(limit: int = 10, *, history_path: Optional[str] = None) -> str:
    rows = list_history(limit=limit, history_path=history_path)
    if not rows: return "(no sandbox history yet)"
    out = []
    for r in rows:
        out.append(f"{r.get('ts','?')} • {r.get('event','?')} • {r.get('status','')}".rstrip())
    return "\n".join(out)
