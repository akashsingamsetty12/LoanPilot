"""
LLM Client Abstraction
=======================
Unified interface for LLM API calls. Supports OpenAI (GPT-4o) and
Anthropic (Claude). Swap providers via config without changing service code.


DESIGN PRINCIPLE: AI/LLMs handle semantic interpretation, extraction,
explanation, and orchestration. Deterministic rules handle facts.
"""

from typing import Optional
from config import get_settings


class LLMClient:
    """
    Abstraction layer over LLM providers.
    Instantiate once, use across classification, extraction, and agent modules.
    """

    def __init__(self):
        settings = get_settings()
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.api_key = settings.OPENAI_API_KEY
        self._client = None

    def _get_client(self):
        """Lazy-initialize the LLM client."""
        if self._client is None:
            if self.provider == "openai":
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            elif self.provider == "anthropic":
                # TODO: Add Anthropic client initialization
                raise NotImplementedError("Anthropic provider not yet implemented")
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        return self._client

    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        response_format: Optional[dict] = None,
    ) -> str:
        """
        Send a prompt to the LLM and return the response text.

        Args:
            prompt: User prompt
            system: System message (optional)
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum response tokens
            response_format: JSON mode config (e.g. {"type": "json_object"})

        Returns:
            LLM response text
        """
        # TODO: Implement LLM call based on self.provider
        raise NotImplementedError(
            "LLMClient.complete() not yet implemented. "
            "LLM client implementation required for this provider."
        )

    async def classify_document(self, text: str) -> dict:
        """
        Classify a document's type using a single LLM prompt.

        Args:
            text: Raw OCR text from the document

        Returns:
            {"type": "payslip", "confidence": 0.95, "reasoning": "..."}
        """
        # TODO: Implement classification prompt
        raise NotImplementedError("classify_document() is not implemented")

    async def extract_fields(self, text: str, doc_type: str) -> dict:
        """
        Extract structured fields from document text using LLM.

        Args:
            text: Raw OCR text from the document
            doc_type: Classified document type

        Returns:
            dict of field_name → {"value": ..., "confidence": ..., "page": ...}
        """
        # TODO: Implement extraction prompt per doc_type
        raise NotImplementedError("extract_fields() is not implemented")


# Singleton instance
llm_client = LLMClient()
