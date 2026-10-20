from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class ExtractedValue[T](BaseModel):
    value: T | None
    content: str | None = None
    confidence: float | None = None


class Money(BaseModel):
    amount: Decimal
    currency_code: str | None = None
    currency_symbol: str | None = None


class Address(BaseModel):
    content: str | None = None
    street_address: str | None = None
    house_number: str | None = None
    po_box: str | None = None
    road: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country_region: str | None = None


class TaxDetail(BaseModel):
    amount: ExtractedValue[Money] | None = None
    rate: ExtractedValue[str] | None = None
    net_amount: ExtractedValue[Money] | None = None
    description: ExtractedValue[str] | None = None
