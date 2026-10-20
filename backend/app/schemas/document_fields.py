"""Map Document Intelligence field dictionaries onto typed values."""

from __future__ import annotations

import logging
from datetime import date, time
from decimal import Decimal
from typing import Any

from app.schemas.common import Address, ExtractedValue, Money

logger = logging.getLogger(__name__)


def field_map(document: dict[str, Any]) -> dict[str, Any]:
    return document.get("fields") or {}


def extracted_string(fields: dict[str, Any], name: str) -> ExtractedValue[str] | None:
    field = fields.get(name)
    if not isinstance(field, dict):
        return None
    value = field.get("valueString")
    if value is None:
        value = field.get("content")
    if value is None:
        return None
    return ExtractedValue(
        value=str(value),
        content=field.get("content"),
        confidence=field.get("confidence"),
    )


def extracted_date(fields: dict[str, Any], name: str) -> ExtractedValue[date] | None:
    field = fields.get(name)
    if not isinstance(field, dict):
        return None
    raw = field.get("valueDate")
    if not raw:
        return _evidence_without_value(field)
    return ExtractedValue(
        value=date.fromisoformat(str(raw)),
        content=field.get("content"),
        confidence=field.get("confidence"),
    )


def extracted_time(fields: dict[str, Any], name: str) -> ExtractedValue[time] | None:
    field = fields.get(name)
    if not isinstance(field, dict):
        return None
    raw = field.get("valueTime")
    if not raw:
        return None
    return ExtractedValue(
        value=time.fromisoformat(str(raw)),
        content=field.get("content"),
        confidence=field.get("confidence"),
    )


def extracted_number(fields: dict[str, Any], name: str) -> ExtractedValue[Decimal] | None:
    field = fields.get(name)
    if not isinstance(field, dict):
        return None
    raw = field.get("valueNumber")
    if raw is None:
        return _evidence_without_value(field)
    return ExtractedValue(
        value=Decimal(str(raw)),
        content=field.get("content"),
        confidence=field.get("confidence"),
    )


def extracted_money(fields: dict[str, Any], name: str) -> ExtractedValue[Money] | None:
    field = fields.get(name)
    if not isinstance(field, dict):
        return None
    return money_from_field(field)


def extracted_address(fields: dict[str, Any], name: str) -> ExtractedValue[Address] | None:
    field = fields.get(name)
    if not isinstance(field, dict):
        return None
    raw = field.get("valueAddress") or {}
    address = Address(
        content=field.get("content"),
        street_address=raw.get("streetAddress"),
        house_number=raw.get("houseNumber"),
        po_box=raw.get("poBox"),
        road=raw.get("road"),
        city=raw.get("city"),
        state=raw.get("state"),
        postal_code=raw.get("postalCode"),
        country_region=raw.get("countryRegion"),
    )
    if not any(
        (
            address.content,
            address.street_address,
            address.house_number,
            address.po_box,
            address.road,
            address.city,
            address.state,
            address.postal_code,
            address.country_region,
        )
    ):
        return None
    return ExtractedValue(
        value=address,
        content=field.get("content"),
        confidence=field.get("confidence"),
    )


def object_list(fields: dict[str, Any], name: str) -> list[dict[str, Any]]:
    field = fields.get(name)
    if field is None:
        return []
    if not isinstance(field, dict):
        logger.warning(
            "Skipping malformed Document Intelligence collection %s: expected an object.",
            name,
        )
        return []
    items = field.get("valueArray")
    if items is None:
        return []
    if not isinstance(items, list):
        logger.warning(
            "Skipping malformed Document Intelligence collection %s: expected an array.",
            name,
        )
        return []

    objects: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            logger.warning(
                "Skipping malformed Document Intelligence %s entry at index %d: "
                "expected an object.",
                name,
                index,
            )
            continue
        value_object = item.get("valueObject")
        if not isinstance(value_object, dict) or not value_object:
            logger.warning(
                "Skipping malformed Document Intelligence %s entry at index %d: "
                "expected a non-empty valueObject.",
                name,
                index,
            )
            continue
        objects.append(value_object)
    return objects


def money_from_field(field: dict[str, Any]) -> ExtractedValue[Money] | None:
    raw = field.get("valueCurrency") or {}
    amount = raw.get("amount")
    if amount is None:
        return _evidence_without_value(field)
    return ExtractedValue(
        value=Money(
            amount=Decimal(str(amount)),
            currency_code=raw.get("currencyCode"),
            currency_symbol=raw.get("currencySymbol"),
        ),
        content=field.get("content"),
        confidence=field.get("confidence"),
    )


def _evidence_without_value[T](field: dict[str, Any]) -> ExtractedValue[T] | None:
    content = field.get("content")
    confidence = field.get("confidence")
    if content is None and confidence is None:
        return None
    return ExtractedValue(
        value=None,
        content=content,
        confidence=confidence,
    )


def first_currency_code(*amounts: ExtractedValue[Money] | None) -> str | None:
    for amount in amounts:
        if amount and amount.value is not None and amount.value.currency_code:
            return amount.value.currency_code
        if amount and amount.value is not None and amount.value.currency_symbol:
            return amount.value.currency_symbol
    return None
