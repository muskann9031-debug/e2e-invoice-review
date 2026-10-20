"""Azure Document Intelligence surface for invoice analysis."""

from __future__ import annotations

from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.core.credentials import AzureKeyCredential

from app.config import Settings

PREBUILT_INVOICE_MODEL = "prebuilt-invoice"
PREBUILT_RECEIPT_MODEL = "prebuilt-receipt"
_CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


class DocumentIntelligenceService:
    def __init__(
        self,
        endpoint: str | None = None,
        key: str | None = None,
    ) -> None:
        settings = Settings()
        resolved_endpoint = (
            endpoint or settings.azure_document_intelligence_endpoint or ""
        ).strip()
        resolved_key = (key or settings.azure_document_intelligence_key or "").strip()
        if not resolved_endpoint:
            raise ValueError("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT is missing.")
        if not resolved_key:
            raise ValueError("AZURE_DOCUMENT_INTELLIGENCE_KEY is missing.")

        self._client = DocumentIntelligenceClient(
            endpoint=resolved_endpoint,
            credential=AzureKeyCredential(resolved_key),
        )

    def analyze_invoice(self, document_path: str | Path) -> AnalyzeResult:
        return self._analyze(document_path, PREBUILT_INVOICE_MODEL)

    def analyze_receipt(self, document_path: str | Path) -> AnalyzeResult:
        return self._analyze(document_path, PREBUILT_RECEIPT_MODEL)

    def _analyze(self, document_path: str | Path, model_id: str) -> AnalyzeResult:
        path = Path(document_path)
        if not path.is_file():
            raise FileNotFoundError(f"Document file not found: {path}")

        content_type = _CONTENT_TYPES.get(path.suffix.lower())
        if content_type is None:
            raise ValueError(f"Unsupported document file type: {path.suffix}")

        with path.open("rb") as document:
            poller = self._client.begin_analyze_document(
                model_id=model_id,
                body=document,
                content_type=content_type,
            )
        return poller.result()
