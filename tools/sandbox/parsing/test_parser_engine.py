# test_parser_engine.py

import sys
sys.path.append("/app")

from parsing.document_parser import extract_text_from_file
from parsing.ocr_reader import extract_text_from_image

def run_test():
    print("[TEST] Document Parser Test")
    doc_path = "/app/parsing/test_docs/sample_doc.txt"  # Replace with an actual path later
    try:
        doc_text = extract_text_from_file(doc_path)
        print(" - Document Text Extracted:")
        print(doc_text[:250] + "...\n")
    except Exception as e:
        print(f" - Document parsing failed: {e}")

    print("[TEST] OCR Reader Test")
    image_path = "/app/parsing/test_docs/sample_image.png"  # Replace with actual image
    try:
        image_text = extract_text_from_image(image_path)
        print(" - Image Text Extracted:")
        print(image_text + "\n")
    except Exception as e:
        print(f" - OCR parsing failed: {e}")

if __name__ == "__main__":
    run_test()
