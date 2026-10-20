"""Azure OpenAI Responses API adapter."""

from __future__ import annotations

from openai import AsyncOpenAI, OpenAI
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.config import Settings
from app.schemas.classification import DocumentClassification

AZURE_OPENAI_MODEL = "gpt-6-astra"
_SUPPORTED_MEDIA_TYPES = {"application/pdf", "image/jpeg", "image/png"}


class AzureOpenAIService:
    def __init__(
        self,
        endpoint: str | None = None,
        api_key: str | None = None,
    ) -> None:
        settings = Settings()
        resolved_endpoint = (endpoint or settings.azure_openai_endpoint or "").strip()
        resolved_api_key = (api_key or settings.azure_openai_api_key or "").strip()
        if not resolved_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is missing.")
        if not resolved_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is missing.")

        self._client = OpenAI(
            base_url=resolved_endpoint.rstrip("/"),
            api_key=resolved_api_key,
        )

    def generate_text(self, prompt: str) -> str:
        response = self._client.responses.create(
            model=AZURE_OPENAI_MODEL,
            input=prompt,
        )
        return response.output_text


class AzureOpenAIClassificationService:
    def __init__(
        self,
        endpoint: str | None = None,
        api_key: str | None = None,
    ) -> None:
        settings = Settings()
        self._endpoint = (endpoint or settings.azure_openai_endpoint or "").strip()
        self._api_key = (api_key or settings.azure_openai_api_key or "").strip()
        if not self._endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is missing.")
        if not self._api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is missing.")

    async def classify_document(
        self,
        document: bytes,
        media_type: str,
    ) -> DocumentClassification:
        if not document:
            raise ValueError("Document content is empty.")
        if media_type not in _SUPPORTED_MEDIA_TYPES:
            raise ValueError(f"Unsupported document media type: {media_type}")

        async with AsyncOpenAI(
            base_url=self._endpoint.rstrip("/"),
            api_key=self._api_key,
        ) as client:
            agent = Agent(
                OpenAIResponsesModel(
                    AZURE_OPENAI_MODEL,
                    provider=OpenAIProvider(openai_client=client),
                ),
                output_type=DocumentClassification,
                instructions=(
                    "Classify the attached document as an invoice, receipt, or other. "
                    "Use 'other' when it is neither an invoice nor a receipt. "
                    "Return a confidence score from 0 to 1."
                ),
            )
            result = await agent.run(
                [
                    "Classify this document.",
                    BinaryContent(data=document, media_type=media_type),
                ]
            )
        return result.output
