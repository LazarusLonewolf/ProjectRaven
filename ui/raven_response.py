# raven_response.py
# Response Formatter for GUI – Project_Raven

def format_response(response_text, mode="default"):
    """Standardizes the format of responses for GUI output."""
    if mode == "default":
        return f"Raven says: {response_text}"
    elif mode == "debug":
        return f"[DEBUG MODE] Response: {response_text}"
    else:
        return f"[{mode.upper()}] {response_text}"
