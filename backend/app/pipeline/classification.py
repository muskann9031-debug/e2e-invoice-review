"""Classification step for incoming financial documents."""

from __future__ import annotations

from app.providers.azure_openai import AzureOpenAIClassificationService
from app.schemas.classification import DocumentClassification


async def classify_document(
    document: bytes,
    media_type: str,
) -> DocumentClassification:
    """Classify a PDF or image as an invoice, receipt, or other document."""
    classifier = AzureOpenAIClassificationService()
    return await classifier.classify_document(document, media_type)
