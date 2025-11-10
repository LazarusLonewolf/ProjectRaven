from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".md", ".rtf"}

def parse_document(path: str) -> dict:
    """
    Minimal API used by sandbox: return {"ok": True/False, "text" or "error": "..."}.
    Heavy deps are imported only inside the function.
    """
    p = Path(path)
    if not p.exists():
        return {"ok": False, "error": f"file not found: {p}"}

    # Try fast path for plain text-like files
    if p.suffix.lower() in {".txt", ".log", ".md"}:
        try:
            return {"ok": True, "text": p.read_text(encoding="utf-8", errors="ignore")}
        except Exception as e2:
            return {"ok": False, "error": f"read error: {e2}"}

    # Fallback to textract for other supported types
    try:
        import textract  # imported lazily
        text = textract.process(str(p)).decode("utf-8", errors="ignore")
        return {"ok": True, "text": text}
    except Exception as e:
        return {"ok": False, "error": f"textract unavailable or failed: {e}"}

# Optional helpers for your own use; kept lazy/defensive
def extract_text_from_file(file_path: str) -> str:
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(file_path)
    if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {p.suffix}")
    res = parse_document(str(p))
    if not res.get("ok"):
        raise RuntimeError(res.get("error", "unknown error"))
    return res["text"]

def parse_text(input_text: str) -> dict:
    lines = input_text.strip().splitlines()
    paragraphs = [p.strip() for p in input_text.split('\n\n') if p.strip()]
    headers = [ln for ln in lines if ln.startswith("#")]
    bullets = [ln for ln in lines if ln.lstrip().startswith(("-", "*", "+"))]

    # crude fenced code detection
    code_blocks, buf, inside = [], [], False
    for ln in lines:
        if ln.strip().startswith("```"):
            if inside:
                code_blocks.append("\n".join(buf)); buf.clear(); inside = False
            else:
                inside = True
        elif inside:
            buf.append(ln)

    return {
        "parsed": True,
        "line_count": len(lines),
        "paragraph_count": len(paragraphs),
        "headers": headers,
        "bullets": bullets,
        "code_blocks": code_blocks,
        "content_preview": lines[:5],
    }
