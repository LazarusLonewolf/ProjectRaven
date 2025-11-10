# tools/sandbox/sandbox_history.py
try:
    from .sandbox_history_tool import log_event, list_history, summarize_history
except Exception:
    def log_event(*args, **kwargs): pass
    def list_history(*args, **kwargs): return []
    def summarize_history(*args, **kwargs): return "(history unavailable)"
