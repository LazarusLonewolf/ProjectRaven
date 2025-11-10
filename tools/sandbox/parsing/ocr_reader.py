# tools/sandbox/parsing/ocr_reader.py
import os, io
from pathlib import Path

# Try PIL (Pillow)
try:
    from PIL import Image, ImageOps
except Exception:
    Image = None

# Try pytesseract (preferred for Windows)
_TESS_OK = False
try:
    import pytesseract
    TESS = os.environ.get("TESSERACT_EXE")  # allow override
    if not TESS:
        # common Windows default
        TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if not Path(TESS).exists():
            # another common path on some installs
            alt = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
            if Path(alt).exists():
                TESS = alt
            else:
                TESS = None
    if TESS:
        pytesseract.pytesseract.tesseract_cmd = TESS
        _TESS_OK = True
except Exception:
    pytesseract = None

def _ensure_image(img_path: str):
    if not Image:
        return None, "[ocr] Pillow (PIL) not available. Install with: pip install pillow"
    try:
        img = Image.open(img_path)
        # safety: convert mode if needed
        if img.mode in ("RGBA", "LA"):
            # flatten transparency onto white
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1])
            img = bg
        elif img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        return img, None
    except Exception as e:
        return None, f"[ocr] Could not open image: {e}"

def ocr_image(image_path: str) -> dict:
    """
    Returns { ok: bool, text: str, error: str|None, engine: 'tesseract'|'none' }
    """
    p = Path(image_path)
    if not p.exists():
        return {"ok": False, "text": "", "error": f"[ocr] file not found: {p}", "engine": "none"}

    # Prefer Tesseract via pytesseract
    if _TESS_OK and pytesseract and Image:
        img, err = _ensure_image(str(p))
        if err:
            return {"ok": False, "text": "", "error": err, "engine": "tesseract"}
        try:
            # simple preproc: boost contrast for screenshots
            # (keep it minimal / reliable)
            gray = ImageOps.grayscale(img)
            text = pytesseract.image_to_string(gray)
            text = (text or "").strip()
            if text:
                return {"ok": True, "text": text, "error": None, "engine": "tesseract"}
            # fall through to explicit error if nothing extracted
            return {"ok": False, "text": "", "error": "[ocr] no text detected", "engine": "tesseract"}
        except Exception as e:
            return {"ok": False, "text": "", "error": f"[ocr] tesseract error: {e}", "engine": "tesseract"}

    # No engine available
    missing = []
    if not Image: missing.append("Pillow")
    if not pytesseract: missing.append("pytesseract")
    if pytesseract and not _TESS_OK: missing.append("tesseract.exe")
    msg = "[ocr] no OCR implementation available"
    if missing:
        msg += " (missing: " + ", ".join(missing) + ")"
    return {"ok": False, "text": "", "error": msg, "engine": "none"}
