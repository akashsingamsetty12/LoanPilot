from typing import List, Optional, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field, model_validator


class DocumentType(str, Enum):
    PAYSLIP = "payslip"
    BANK_STATEMENT = "bank_statement"
    TAX_RETURN = "tax_return"
    KYC_IDENTITY = "kyc_identity"
    ADDRESS_PROOF = "address_proof"
    OTHER = "other"


# --- Input Schemas ---

class OCRPage(BaseModel):
    page: int = Field(..., description="1-indexed page number")
    text: str = Field(..., description="Extracted text from OCR for this page")
    ocr_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="OCR engine confidence score")


class OCRDocumentInput(BaseModel):
    document_id: str = Field(..., description="Unique document identifier")
    filename: Optional[str] = Field(default=None, description="Original filename of the document")
    pages: List[OCRPage] = Field(..., min_length=1, description="List of OCR page data")
    ocr_confidence: Optional[float] = Field(default=None, description="Overall OCR confidence")

    @model_validator(mode="after")
    def compute_ocr_confidence(self) -> "OCRDocumentInput":
        if self.ocr_confidence is None and self.pages:
            confidences = [p.ocr_confidence for p in self.pages if p.ocr_confidence is not None]
            if confidences:
                self.ocr_confidence = round(sum(confidences) / len(confidences), 4)
            else:
                self.ocr_confidence = 1.0
        return self


# --- Output Base Field Schema ---

class ExtractedField(BaseModel):
    value: Optional[Any] = Field(default=None, description="Extracted value (string, float, int, etc.)")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Extraction confidence score (0.0 to 1.0)")
    page: Optional[int] = Field(default=None, description="Page number where the field was found")
    needs_review: bool = Field(default=False, description="Flagged for manual review if low confidence or missing")


# --- Classification Schema ---

class ClassificationResult(BaseModel):
    document_id: str = Field(..., description="Target document ID")
    document_type: DocumentType = Field(..., description="Classified document category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    reason: str = Field(..., description="LLM rationale for the assigned classification")


# --- Document Specific Field Schemas ---

class PayslipFields(BaseModel):
    name: ExtractedField = Field(default_factory=ExtractedField)
    employer: ExtractedField = Field(default_factory=ExtractedField)
    pay_period: ExtractedField = Field(default_factory=ExtractedField)
    gross_salary: ExtractedField = Field(default_factory=ExtractedField)
    net_salary: ExtractedField = Field(default_factory=ExtractedField)


class BankStatementFields(BaseModel):
    account_holder: ExtractedField = Field(default_factory=ExtractedField)
    bank: ExtractedField = Field(default_factory=ExtractedField)
    statement_period: ExtractedField = Field(default_factory=ExtractedField)
    salary_credits: ExtractedField = Field(default_factory=ExtractedField)
    average_monthly_credit: ExtractedField = Field(default_factory=ExtractedField)


class TaxReturnFields(BaseModel):
    taxpayer_name: ExtractedField = Field(default_factory=ExtractedField)
    assessment_year: ExtractedField = Field(default_factory=ExtractedField)
    declared_income: ExtractedField = Field(default_factory=ExtractedField)


class KYCIdentityFields(BaseModel):
    name: ExtractedField = Field(default_factory=ExtractedField)
    DOB: ExtractedField = Field(default_factory=ExtractedField)
    address: ExtractedField = Field(default_factory=ExtractedField)
    ID_number: ExtractedField = Field(default_factory=ExtractedField)


class AddressProofFields(BaseModel):
    name: ExtractedField = Field(default_factory=ExtractedField)
    address: ExtractedField = Field(default_factory=ExtractedField)
    document_issuer: ExtractedField = Field(default_factory=ExtractedField)
    issue_date: ExtractedField = Field(default_factory=ExtractedField)


# --- Unified Canonical Output Schema ---

class ExtractionResult(BaseModel):
    document_id: str
    document_type: DocumentType
    type: DocumentType  # Duplicate / alias for full API compatibility with 'type' vs 'document_type'
    filename: Optional[str] = None
    ocr_confidence: Optional[float] = None
    fields: Dict[str, ExtractedField] = Field(default_factory=dict)
