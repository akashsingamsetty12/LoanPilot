"""
Document Classification Service
============================================
Identifies each document's type using a single well-designed LLM prompt.


GOLDEN RULE: Use ONE well-designed LLM prompt, not a custom ML classifier.

Data flow:
  Raw text → LLM classification → doc_type + confidence

Supported types:
  payslip | bank_statement | tax_return | kyc_identity | address_proof | other

Input:  Document.raw_text
Output: Document.doc_type and Document.classification_confidence updated in DB
"""

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.extraction import ClassificationResult


async def classify_document(doc_id: str, db: AsyncSession) -> ClassificationResult:
    """
    Classify a document's type using LLM.

    Steps:
      1. Load Document.raw_text from DB
      2. Build LLM prompt:
         "Given the following document text, classify it as one of:
          payslip, bank_statement, tax_return, kyc_identity, address_proof, other.
          Return JSON: {type, confidence, reasoning}"
      3. Call LLM via utils/llm_client.py
      4. Parse response
      5. Update Document.doc_type and Document.classification_confidence in DB
      6. Update Document.status = "classified"
      7. Return ClassificationResult

    TODO: implement LLM classification prompt
    """
    raise NotImplementedError("classify_document() is not implemented")
