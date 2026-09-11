"""
OCR & Document Understanding Service
====================================

Converts uploaded PDF/image documents into machine-readable text
with page-level and block-level evidence.

Supported:
    - PDF
    - JPG
    - JPEG
    - PNG

Technologies:
    - PyMuPDF: digital PDF text extraction
    - Tesseract + Pillow: scanned/image OCR

Output:
    Document.raw_text = [
        {
            "page": 1,
            "text": "...",
            "confidence": 0.94,
            "evidence": [...]
        }
    ]
"""

import os

import pymupdf
import pytesseract

from PIL import Image, ImageOps, ImageFilter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.document import Document


# ---------------------------------------------------------
# TESSERACT CONFIGURATION
# ---------------------------------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# ---------------------------------------------------------
# OCR CONFIDENCE
# ---------------------------------------------------------

def calculate_ocr_confidence(data: dict) -> float:
    """
    Calculate average OCR confidence from detected text words.

    Tesseract confidence values are 0-100.
    We convert them to 0.0-1.0.
    """

    confidences = []

    for text, conf in zip(data["text"], data["conf"]):

        text = text.strip()

        try:
            value = float(conf)

            if text and value >= 0:
                confidences.append(value)

        except (ValueError, TypeError):
            continue

    if not confidences:
        return 0.0

    return round(
        sum(confidences) / len(confidences) / 100,
        2
    )


# ---------------------------------------------------------
# IMAGE PREPROCESSING
# ---------------------------------------------------------

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Improve image quality before OCR.

    Steps:
        1. Convert to RGB
        2. Convert to grayscale
        3. Upscale 2x
        4. Improve contrast
        5. Apply light denoising
    """

    image = image.convert("RGB")

    image = ImageOps.grayscale(image)

    width, height = image.size

    image = image.resize(
        (width * 2, height * 2)
    )

    image = ImageOps.autocontrast(image)

    image = image.filter(
        ImageFilter.MedianFilter(size=3)
    )

    return image


# ---------------------------------------------------------
# OCR SINGLE IMAGE
# ---------------------------------------------------------

def ocr_image(
    image: Image.Image,
    page_number: int,
    document_id: str | None = None
) -> dict:
    """
    Perform OCR on one image/page.

    Returns:
        page number
        extracted text
        OCR confidence
        source evidence
    """

    processed_image = preprocess_image(image)

    data = pytesseract.image_to_data(
        processed_image,
        output_type=pytesseract.Output.DICT,
        config="--psm 6"
    )

    text_parts = []
    evidence = []

    for i, raw_text in enumerate(data["text"]):

        text = raw_text.strip()

        if not text:
            continue

        try:
            confidence = float(data["conf"][i])

        except (ValueError, TypeError):
            confidence = -1

        if confidence < 0:
            continue

        text_parts.append(text)

        evidence.append(
            {
                "document_id": document_id,
                "page_number": page_number,
                "text": text,
                "confidence": round(
                    confidence / 100,
                    2
                ),
                "bounding_box": {
                    "x": data["left"][i],
                    "y": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i]
                }
            }
        )

    text = " ".join(text_parts)

    confidence = calculate_ocr_confidence(data)

    return {
        "page": page_number,
        "text": text,
        "confidence": confidence,
        "evidence": evidence
    }


# ---------------------------------------------------------
# PDF EXTRACTION
# ---------------------------------------------------------

async def extract_text_from_pdf(
    file_path: str
) -> list[dict]:
    """
    Process PDF page by page.

    Digital/selectable PDF:
        Extract text directly using PyMuPDF.

    Scanned/image PDF:
        Render page as image and use Tesseract OCR.
    """

    pdf = pymupdf.open(file_path)

    pages = []

    try:

        for page_index, page in enumerate(pdf):

            page_number = page_index + 1

            # ---------------------------------------------
            # TRY DIGITAL PDF TEXT FIRST
            # ---------------------------------------------

            text = page.get_text().strip()

            if text:

                pages.append(
                    {
                        "page": page_number,
                        "text": text,
                        "confidence": 1.0,
                        "extraction_method": "pymupdf",
                        "evidence": [
                            {
                                "page_number": page_number,
                                "text": text,
                                "confidence": 1.0
                            }
                        ]
                    }
                )

            # ---------------------------------------------
            # SCANNED PDF
            # ---------------------------------------------

            else:

                pix = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False
                )

                image_bytes = pix.tobytes("png")

                import io

                image = Image.open(
                    io.BytesIO(image_bytes)
                )

                result = ocr_image(
                    image,
                    page_number
                )

                result["extraction_method"] = "tesseract"

                pages.append(result)

    finally:

        pdf.close()

    return pages


# ---------------------------------------------------------
# IMAGE EXTRACTION
# ---------------------------------------------------------

async def extract_text_from_image(
    file_path: str
) -> list[dict]:
    """
    Extract text from JPG/JPEG/PNG using Tesseract.
    """

    image = Image.open(file_path)

    try:

        result = ocr_image(
            image,
            page_number=1
        )

        result["extraction_method"] = "tesseract"

        return [result]

    finally:

        image.close()


# ---------------------------------------------------------
# MAIN DOCUMENT PROCESSOR
# ---------------------------------------------------------

async def process_document(
    doc_id: str,
    db: AsyncSession
) -> dict:
    """
    Main Module 3 entry point.

    1. Load Document from database.
    2. Read file_path.
    3. Detect file type.
    4. Extract text.
    5. Add document/page evidence.
    6. Calculate average confidence.
    7. Update database.
    8. Mark OCR as complete.

    On failure:
        status = "failed"
        error_message = error details
    """

    # -----------------------------------------------------
    # LOAD DOCUMENT
    # -----------------------------------------------------

    result = await db.execute(
        select(Document).where(
            Document.id == doc_id
        )
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise ValueError(
            f"Document not found: {doc_id}"
        )

    # -----------------------------------------------------
    # START OCR
    # -----------------------------------------------------

    document.status = "ocr_processing"
    document.error_message = None

    await db.commit()

    try:

        file_path = document.file_path

        if not os.path.exists(file_path):

            raise FileNotFoundError(
                f"Document file not found: {file_path}"
            )

        extension = os.path.splitext(
            document.filename
        )[1].lower()

        # -------------------------------------------------
        # PDF
        # -------------------------------------------------

        if extension == ".pdf":

            pages = await extract_text_from_pdf(
                file_path
            )

        # -------------------------------------------------
        # IMAGE
        # -------------------------------------------------

        elif extension in [
            ".jpg",
            ".jpeg",
            ".png"
        ]:

            pages = await extract_text_from_image(
                file_path
            )

        # -------------------------------------------------
        # UNSUPPORTED
        # -------------------------------------------------

        else:

            raise ValueError(
                "Unsupported file type. "
                "Use PDF, JPG, JPEG or PNG."
            )

        # -------------------------------------------------
        # ADD DOCUMENT ID TO EVIDENCE
        # -------------------------------------------------

        for page in pages:

            page["document_id"] = document.id

            page["filename"] = document.filename

            page["source"] = {
                "document_id": document.id,
                "filename": document.filename,
                "page_number": page["page"]
            }

            for evidence_item in page.get(
                "evidence",
                []
            ):

                evidence_item[
                    "document_id"
                ] = document.id

                evidence_item[
                    "page_number"
                ] = page["page"]

        # -------------------------------------------------
        # CALCULATE AVERAGE CONFIDENCE
        # -------------------------------------------------

        confidence_values = [
            page["confidence"]
            for page in pages
            if page.get("confidence") is not None
        ]

        if confidence_values:

            average_confidence = round(
                sum(confidence_values)
                / len(confidence_values),
                2
            )

        else:

            average_confidence = 0.0

        # -------------------------------------------------
        # UPDATE DATABASE
        # -------------------------------------------------

        document.raw_text = pages

        document.pages = len(pages)

        document.ocr_confidence = (
            average_confidence
        )

        document.status = "ocr_complete"

        document.error_message = None

        await db.commit()

        # -------------------------------------------------
        # RETURN RESULT
        # -------------------------------------------------

        return {
            "document_id": document.id,
            "filename": document.filename,
            "pages": len(pages),
            "ocr_confidence": average_confidence,
            "status": "ocr_complete"
        }

    # -----------------------------------------------------
    # ERROR HANDLING
    # -----------------------------------------------------

    except Exception as error:

        document.status = "failed"

        document.error_message = str(error)

        await db.commit()

        raise RuntimeError(
            f"OCR processing failed: {error}"
        ) from error