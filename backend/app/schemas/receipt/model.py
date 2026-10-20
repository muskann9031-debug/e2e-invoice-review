from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import Any, Self

from pydantic import BaseModel, Field

from app.schemas.common import Address, ExtractedValue, Money, TaxDetail
from app.schemas.document_fields import (
    extracted_address,
    extracted_date,
    extracted_money,
    extracted_number,
    extracted_string,
    extracted_time,
    field_map,
    first_currency_code,
    object_list,
)


class ReceiptLineItem(BaseModel):
    description: ExtractedValue[str] | None = None
    quantity: ExtractedValue[Decimal] | None = None
    quantity_unit: ExtractedValue[str] | None = None
    price: ExtractedValue[Money] | None = None
    total_price: ExtractedValue[Money] | None = None
    product_code: ExtractedValue[str] | None = None


class ReceiptPayment(BaseModel):
    method: ExtractedValue[str] | None = None
    amount: ExtractedValue[Money] | None = None


class Receipt(BaseModel):
    """Typed receipt fields from Azure Document Intelligence `prebuilt-receipt`."""

    doc_type: str | None = None
    confidence: float | None = None
    merchant_name: ExtractedValue[str] | None = None
    merchant_phone_number: ExtractedValue[str] | None = None
    merchant_address: ExtractedValue[Address] | None = None
    transaction_date: ExtractedValue[date] | None = None
    transaction_time: ExtractedValue[time] | None = None
    receipt_type: ExtractedValue[str] | None = None
    country_region: ExtractedValue[str] | None = None
    currency: str | None = None
    subtotal: ExtractedValue[Money] | None = None
    total_tax: ExtractedValue[Money] | None = None
    tip: ExtractedValue[Money] | None = None
    total: ExtractedValue[Money] | None = None
    items: list[ReceiptLineItem] = Field(default_factory=list)
    payments: list[ReceiptPayment] = Field(default_factory=list)
    tax_details: list[TaxDetail] = Field(default_factory=list)

    @classmethod
    def from_document_intelligence(cls, document: dict[str, Any]) -> Self:
        fields = field_map(document)
        subtotal = extracted_money(fields, "Subtotal")
        total_tax = extracted_money(fields, "TotalTax")
        tip = extracted_money(fields, "Tip")
        total = extracted_money(fields, "Total")
        country_value = _country_region(fields)
        return cls(
            doc_type=document.get("docType"),
            confidence=document.get("confidence"),
            merchant_name=extracted_string(fields, "MerchantName"),
            merchant_phone_number=_phone_number(fields),
            merchant_address=extracted_address(fields, "MerchantAddress"),
            transaction_date=extracted_date(fields, "TransactionDate"),
            transaction_time=extracted_time(fields, "TransactionTime"),
            receipt_type=extracted_string(fields, "ReceiptType"),
            country_region=country_value,
            currency=first_currency_code(total, subtotal, total_tax, tip),
            subtotal=subtotal,
            total_tax=total_tax,
            tip=tip,
            total=total,
            items=[
                ReceiptLineItem(
                    description=extracted_string(item, "Description"),
                    quantity=extracted_number(item, "Quantity"),
                    quantity_unit=extracted_string(item, "QuantityUnit"),
                    price=extracted_money(item, "Price"),
                    total_price=extracted_money(item, "TotalPrice"),
                    product_code=extracted_string(item, "ProductCode"),
                )
                for item in object_list(fields, "Items")
            ],
            payments=[
                ReceiptPayment(
                    method=extracted_string(payment, "Method"),
                    amount=extracted_money(payment, "Amount"),
                )
                for payment in object_list(fields, "Payments")
            ],
            tax_details=[
                TaxDetail(
                    amount=extracted_money(detail, "Amount"),
                    rate=_rate(detail),
                    net_amount=extracted_money(detail, "NetAmount"),
                    description=extracted_string(detail, "Description"),
                )
                for detail in object_list(fields, "TaxDetails")
            ],
        )


def _phone_number(fields: dict[str, Any]) -> ExtractedValue[str] | None:
    field = fields.get("MerchantPhoneNumber")
    if not isinstance(field, dict):
        return None
    value = field.get("valuePhoneNumber") or field.get("content")
    if value is None:
        return None
    return ExtractedValue(
        value=str(value),
        content=field.get("content"),
        confidence=field.get("confidence"),
    )


def _country_region(fields: dict[str, Any]) -> ExtractedValue[str] | None:
    field = fields.get("CountryRegion")
    if not isinstance(field, dict):
        return None
    raw = field.get("valueCountryRegion") or field.get("content")
    if raw is None:
        return None
    return ExtractedValue(
        value=str(raw),
        content=field.get("content"),
        confidence=field.get("confidence"),
    )


def _rate(fields: dict[str, Any]) -> ExtractedValue[str] | None:
    number = extracted_number(fields, "Rate")
    if number is not None and number.value is not None:
        return ExtractedValue(
            value=str(number.value),
            content=number.content,
            confidence=number.confidence,
        )
    return extracted_string(fields, "Rate")
