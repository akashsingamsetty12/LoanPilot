"""
Evidence Trail Builder
=======================
Standardized evidence formatting for every extracted field and flag.
Used by Modules 3–7 to maintain source traceability.

DESIGN PRINCIPLE: Every extracted field and every flag carries evidence —
source document, page, and confidence.
"""


class EvidenceBuilder:
    """Builds standardized evidence strings for traceability."""

    @staticmethod
    def field_evidence(doc_id: str, page: int, confidence: float) -> str:
        """
        Build evidence for a single extracted field.

        Args:
            doc_id: Document ID (e.g. "DOC-0001")
            page: Source page number (1-indexed)
            confidence: Extraction confidence (0.0–1.0)

        Returns:
            e.g. "DOC-0001 p.1 (confidence: 0.97)"
        """
        return f"{doc_id} p.{page} (confidence: {confidence:.2f})"

    @staticmethod
    def comparison_evidence(
        doc1_id: str, page1: int,
        doc2_id: str, page2: int,
    ) -> str:
        """
        Build evidence for a cross-document comparison.

        Returns:
            e.g. "DOC-0001 p.1 vs DOC-0003 p.2"
        """
        return f"{doc1_id} p.{page1} vs {doc2_id} p.{page2}"

    @staticmethod
    def missing_document_evidence(
        doc_type: str,
        required_types: list[str],
        present_types: list[str],
    ) -> str:
        """
        Build evidence for a missing document flag.

        Returns:
            e.g. "Required: payslip, bank_statement, tax_return, kyc_identity. Missing: address_proof"
        """
        missing = set(required_types) - set(present_types)
        return f"Required: {', '.join(required_types)}. Missing: {', '.join(missing)}"
