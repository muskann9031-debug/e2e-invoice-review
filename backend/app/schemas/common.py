from __future__ import annotations

import logging
from datetime import date, time
from decimal import Decimal
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExtractedString(BaseModel):
    value: str | None = None
    content: str | None = None
    confidence: float | None = None


class ExtractedDate(BaseModel):
    value: date | None = None
    content: str | None = None
    confidence: float | None = None


class ExtractedTime(BaseModel):
    value: time | None = None
    content: str | None = None
    confidence: float | None = None


class ExtractedMoney(BaseModel):
    amount: Decimal | None = None
    currency_code: str | None = None
    content: str | None = None
    confidence: float | None = None


class ExtractedAddress(BaseModel):
    content: str | None = None
    confidence: float | None = None


class ExtractedNumber(BaseModel):
    value: Decimal | None = None
    content: str | None = None
    confidence: float | None = None


class TaxDetail(BaseModel):
    amount: ExtractedMoney | None = None
    rate: ExtractedString | None = None


def _field_confidence(field: dict[str, Any] | None) -> float | None:
    if not field:
        return None
    confidence = field.get("confidence")
    return float(confidence) if confidence is not None else None


def parse_string_field(field: dict[str, Any] | None) -> ExtractedString | None:
    if not field:
        return None
    return ExtractedString(
        value=field.get("valueString") or field.get("content"),
        content=field.get("content"),
        confidence=_field_confidence(field),
    )


def parse_date_field(field: dict[str, Any] | None) -> ExtractedDate | None:
    if not field:
        return None
    raw_value = field.get("valueDate")
    parsed: date | None = None
    if raw_value:
        parsed = date.fromisoformat(str(raw_value))
    return ExtractedDate(
        value=parsed,
        content=field.get("content"),
        confidence=_field_confidence(field),
    )


def parse_time_field(field: dict[str, Any] | None) -> ExtractedTime | None:
    if not field:
        return None
    raw_value = field.get("valueTime")
    parsed: time | None = None
    if raw_value:
        parsed = time.fromisoformat(str(raw_value))
    return ExtractedTime(
        value=parsed,
        content=field.get("content"),
        confidence=_field_confidence(field),
    )


def parse_currency_field(field: dict[str, Any] | None) -> ExtractedMoney | None:
    if not field:
        return None
    value_currency = field.get("valueCurrency") or {}
    amount = value_currency.get("amount")
    return ExtractedMoney(
        amount=Decimal(str(amount)) if amount is not None else None,
        currency_code=value_currency.get("currencyCode"),
        content=field.get("content"),
        confidence=_field_confidence(field),
    )


def parse_address_field(field: dict[str, Any] | None) -> ExtractedAddress | None:
    if not field:
        return None
    return ExtractedAddress(
        content=field.get("content"),
        confidence=_field_confidence(field),
    )


def parse_number_field(field: dict[str, Any] | None) -> ExtractedNumber | None:
    if not field:
        return None
    raw_value = field.get("valueNumber")
    return ExtractedNumber(
        value=Decimal(str(raw_value)) if raw_value is not None else None,
        content=field.get("content"),
        confidence=_field_confidence(field),
    )


def parse_array_field(field: Any, field_name: str) -> list[Any]:
    if field is None:
        return []
    if not isinstance(field, dict):
        logger.warning(
            "Skipping malformed Document Intelligence collection %s: expected an object.",
            field_name,
        )
        return []
    items = field.get("valueArray")
    if items is None:
        return []
    if not isinstance(items, list):
        logger.warning(
            "Skipping malformed Document Intelligence collection %s: expected an array.",
            field_name,
        )
        return []
    return items


def parse_object_array_field(field: Any, field_name: str) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    for index, item in enumerate(parse_array_field(field, field_name)):
        if not isinstance(item, dict):
            logger.warning(
                "Skipping malformed Document Intelligence %s entry at index %d: "
                "expected an object.",
                field_name,
                index,
            )
            continue
        value_object = item.get("valueObject")
        if not isinstance(value_object, dict) or not value_object:
            logger.warning(
                "Skipping malformed Document Intelligence %s entry at index %d: "
                "expected a non-empty valueObject.",
                field_name,
                index,
            )
            continue
        objects.append(value_object)
    return objects


def _collect_confidences(value: BaseModel, confidences: list[float]) -> None:
    confidence = getattr(value, "confidence", None)
    if confidence is not None:
        confidences.append(float(confidence))
        return
    for field_name in value.model_fields:
        nested = getattr(value, field_name)
        if isinstance(nested, BaseModel):
            _collect_confidences(nested, confidences)
        elif isinstance(nested, list):
            for item in nested:
                if isinstance(item, BaseModel):
                    _collect_confidences(item, confidences)


def scalar_confidences(model: BaseModel) -> list[float]:
    confidences: list[float] = []
    for field_name in model.model_fields:
        value = getattr(model, field_name)
        if isinstance(value, BaseModel):
            _collect_confidences(value, confidences)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, BaseModel):
                    _collect_confidences(item, confidences)
    return confidences


def average_confidence(model: BaseModel) -> float | None:
    confidences = scalar_confidences(model)
    if not confidences:
        return None
    return sum(confidences) / len(confidences)


def minimum_confidence(model: BaseModel) -> float | None:
    confidences = scalar_confidences(model)
    if not confidences:
        return None
    return min(confidences)
