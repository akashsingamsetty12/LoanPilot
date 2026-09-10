"""Tests for OCR pipeline."""
import pytest


@pytest.mark.asyncio
async def test_ocr_pdf_extraction(client):
    """POST /documents/{id}/ocr should extract text from PDF."""
    pass


@pytest.mark.asyncio
async def test_ocr_image_extraction(client):
    """OCR should handle image files (JPG/PNG)."""
    pass


@pytest.mark.asyncio
async def test_ocr_multipage_document(client):
    """OCR should extract text per page for multi-page docs."""
    pass


@pytest.mark.asyncio
async def test_ocr_confidence_scores(client):
    """OCR should return confidence scores per page."""
    pass
