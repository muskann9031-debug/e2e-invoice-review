"""Provider-independent output for financial document classification."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class DocumentClassification(BaseModel):
    document_type: Literal["invoice", "receipt", "other"]
    confidence: float = Field(ge=0, le=1)
