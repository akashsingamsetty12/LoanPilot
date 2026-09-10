"""
OCR & Document Understanding Service
=================================================
Converts uploaded documents into machine-readable text with
page-level evidence (page number, OCR confidence).


Data flow:
  Document (PDF/image) → raw text + page number + OCR confidence

Technologies:
  - PyMuPDF (fitz): for digital/selectable PDF text
  - Tesseract + Pillow: for scanned/image documents

EVIDENCE RULE: Every text block must carry (document_id, page_number, confidence).

Input:  Document record from DB (file_path on disk)
Output: Document.raw_text updated as JSON:
        [{"page": 1, "text": "...", "confidence": 0.94}, ...]
"""

from sqlalchemy.ext.asyncio import AsyncSession


async def process_document(doc_id: str, db: AsyncSession) -> dict:
    """
    Run OCR on a single document and store results.

    Steps:
      1. Load document file from disk (using Document.file_path)
      2. Detect if PDF has selectable text → use PyMuPDF (fitz)
      3. If scanned/image → preprocess with Pillow, run pytesseract
      4. For multi-page docs: extract text per page separately
      5. Calculate OCR confidence per page and average
      6. Update Document in DB:
         - raw_text = [{"page": 1, "text": "...", "confidence": 0.94}, ...]
         - pages = number of pages
         - ocr_confidence = average confidence
         - status = "ocr_complete"
      7. Return {"document_id": doc_id, "pages": N, "ocr_confidence": avg}

    On failure:
      - Set Document.status = "failed"
      - Set Document.error_message = error details

    TODO: implement OCR pipeline
    """
    raise NotImplementedError("process_document() is not implemented")


async def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF using PyMuPDF (fitz).

    Returns:
      [{"page": 1, "text": "...", "confidence": 1.0}, ...]
      (confidence=1.0 for selectable text since it's already digital)

    TODO: implement PDF text extraction
    """
    raise NotImplementedError("extract_text_from_pdf() is not implemented")


async def extract_text_from_image(file_path: str) -> list[dict]:
    """
    Extract text from an image using Tesseract OCR.

    Steps:
      1. Open image with Pillow
      2. Preprocess: convert to grayscale, threshold, denoise (optional)
      3. Run pytesseract.image_to_data() for text + confidence
      4. Return [{"page": 1, "text": "...", "confidence": 0.87}]

    TODO: implement image OCR
    """
    raise NotImplementedError("extract_text_from_image() is not implemented")
