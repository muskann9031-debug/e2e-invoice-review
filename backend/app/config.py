"""Backend settings loaded from environment variables and the local .env file."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    azure_document_intelligence_endpoint: str | None = None
    azure_document_intelligence_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
