# ocr_extraction_stub.py
# Phase 5 – Document Parser Layer Extension: OCR Extraction for Screenshot Text

import pytesseract
from PIL import Image
import os

def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return f"[ERROR] Unable to process image: {e}"

if __name__ == "__main__":
    test_image = "sample_screenshot.png"
    if os.path.exists(test_image):
        print("[TEST] Extracting text from screenshot...")
        result = extract_text_from_image(test_image)
        print("[RESULT] Text Extracted:")
        print(result)
    else:
        print("[ERROR] Test image not found.")