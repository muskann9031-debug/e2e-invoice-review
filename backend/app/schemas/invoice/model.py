from __future__ import annotations

from datetime import date
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
    field_map,
    first_currency_code,
    object_list,
)


class InvoiceLineItem(BaseModel):
    description: ExtractedValue[str] | None = None
    quantity: ExtractedValue[Decimal] | None = None
    unit: ExtractedValue[str] | None = None
    unit_price: ExtractedValue[Money] | None = None
    amount: ExtractedValue[Money] | None = None
    product_code: ExtractedValue[str] | None = None
    tax: ExtractedValue[Money] | None = None
    tax_rate: ExtractedValue[str] | None = None
    date: ExtractedValue[date] | None = None


class Invoice(BaseModel):
    """Typed invoice fields from Azure Document Intelligence `prebuilt-invoice`."""

    doc_type: str | None = None
    confidence: float | None = None
    vendor_name: ExtractedValue[str] | None = None
    vendor_tax_id: ExtractedValue[str] | None = None
    vendor_address: ExtractedValue[Address] | None = None
    customer_name: ExtractedValue[str] | None = None
    customer_tax_id: ExtractedValue[str] | None = None
    customer_address: ExtractedValue[Address] | None = None
    invoice_id: ExtractedValue[str] | None = None
    invoice_date: ExtractedValue[date] | None = None
    due_date: ExtractedValue[date] | None = None
    purchase_order: ExtractedValue[str] | None = None
    payment_term: ExtractedValue[str] | None = None
    currency: str | None = None
    subtotal: ExtractedValue[Money] | None = None
    total_discount: ExtractedValue[Money] | None = None
    total_tax: ExtractedValue[Money] | None = None
    invoice_total: ExtractedValue[Money] | None = None
    amount_due: ExtractedValue[Money] | None = None
    items: list[InvoiceLineItem] = Field(default_factory=list)
    tax_details: list[TaxDetail] = Field(default_factory=list)

    @classmethod
    def from_document_intelligence(cls, document: dict[str, Any]) -> Self:
        fields = field_map(document)
        subtotal = extracted_money(fields, "SubTotal")
        total_tax = extracted_money(fields, "TotalTax")
        invoice_total = extracted_money(fields, "InvoiceTotal")
        amount_due = extracted_money(fields, "AmountDue")
        total_discount = extracted_money(fields, "TotalDiscount")
        return cls(
            doc_type=document.get("docType"),
            confidence=document.get("confidence"),
            vendor_name=extracted_string(fields, "VendorName"),
            vendor_tax_id=extracted_string(fields, "VendorTaxId"),
            vendor_address=extracted_address(fields, "VendorAddress"),
            customer_name=extracted_string(fields, "CustomerName"),
            customer_tax_id=extracted_string(fields, "CustomerTaxId"),
            customer_address=extracted_address(fields, "CustomerAddress"),
            invoice_id=extracted_string(fields, "InvoiceId"),
            invoice_date=extracted_date(fields, "InvoiceDate"),
            due_date=extracted_date(fields, "DueDate"),
            purchase_order=extracted_string(fields, "PurchaseOrder"),
            payment_term=extracted_string(fields, "PaymentTerm"),
            currency=first_currency_code(invoice_total, subtotal, total_tax, amount_due),
            subtotal=subtotal,
            total_discount=total_discount,
            total_tax=total_tax,
            invoice_total=invoice_total,
            amount_due=amount_due,
            items=[
                InvoiceLineItem(
                    description=extracted_string(item, "Description"),
                    quantity=extracted_number(item, "Quantity"),
                    unit=extracted_string(item, "Unit"),
                    unit_price=extracted_money(item, "UnitPrice"),
                    amount=extracted_money(item, "Amount"),
                    product_code=extracted_string(item, "ProductCode"),
                    tax=extracted_money(item, "Tax"),
                    tax_rate=extracted_string(item, "TaxRate"),
                    date=extracted_date(item, "Date"),
                )
                for item in object_list(fields, "Items")
            ],
            tax_details=[
                TaxDetail(
                    amount=extracted_money(detail, "Amount"),
                    rate=extracted_string(detail, "Rate"),
                )
                for detail in object_list(fields, "TaxDetails")
            ],
        )
