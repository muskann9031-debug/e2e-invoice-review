"""Map Document Intelligence output onto invoice and receipt Pydantic models."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLAYGROUND_DIR = Path(__file__).resolve().parent
REPO_ROOT = PLAYGROUND_DIR.parent
BACKEND_DIR = REPO_ROOT / "backend"
SAMPLES_DIR = REPO_ROOT / "samples" / "generated"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.invoice import Invoice  # noqa: E402
from app.schemas.receipt import Receipt  # noqa: E402
from app.services.document_intelligent_services import DocumentIntelligenceService  # noqa: E402

INVOICE_HAPPY_PATH = SAMPLES_DIR / "01-en-happy-classic.pdf"
INVOICE_MISSING_VENDOR_VAT = SAMPLES_DIR / "05-nl-missing-vendor-vat.pdf"
FUEL_RECEIPT = SAMPLES_DIR / "13-nl-fuel-receipt.png"


def dump_model(model: Invoice | Receipt) -> None:
    print(json.dumps(model.model_dump(mode="json"), indent=2, default=str))


def summarize_invoice(label: str, invoice: Invoice, expected: dict[str, str | None]) -> None:
    print(f"\n=== {label} ===")
    mapped = {
        "vendor_name": (
            invoice.vendor_name.value
            if invoice.vendor_name and invoice.vendor_name.value is not None
            else None
        ),
        "vendor_vat_id": (
            invoice.vendor_tax_id.value
            if invoice.vendor_tax_id and invoice.vendor_tax_id.value is not None
            else None
        ),
        "customer_name": (
            invoice.customer_name.value
            if invoice.customer_name and invoice.customer_name.value is not None
            else None
        ),
        "customer_vat_id": (
            invoice.customer_tax_id.value
            if invoice.customer_tax_id and invoice.customer_tax_id.value is not None
            else None
        ),
        "invoice_number": (
            invoice.invoice_id.value
            if invoice.invoice_id and invoice.invoice_id.value is not None
            else None
        ),
        "invoice_date": (
            invoice.invoice_date.value.isoformat()
            if invoice.invoice_date and invoice.invoice_date.value is not None
            else None
        ),
        "due_date": (
            invoice.due_date.value.isoformat()
            if invoice.due_date and invoice.due_date.value is not None
            else None
        ),
        "purchase_order": (
            invoice.purchase_order.value
            if invoice.purchase_order and invoice.purchase_order.value is not None
            else None
        ),
        "currency": invoice.currency,
        "subtotal": (
            str(invoice.subtotal.value.amount)
            if invoice.subtotal and invoice.subtotal.value is not None
            else None
        ),
        "total_tax": (
            str(invoice.total_tax.value.amount)
            if invoice.total_tax and invoice.total_tax.value is not None
            else None
        ),
        "invoice_total": (
            str(invoice.invoice_total.value.amount)
            if invoice.invoice_total and invoice.invoice_total.value is not None
            else None
        ),
        "item_count": len(invoice.items),
    }
    print(json.dumps(mapped, indent=2))
    print("manifest comparison:")
    for key, expected_value in expected.items():
        actual = mapped.get(key)
        print(f"  {key}: expected={expected_value!r} mapped={actual!r}")


def summarize_receipt(label: str, receipt: Receipt, expected: dict[str, str | None]) -> None:
    print(f"\n=== {label} ===")
    mapped = {
        "merchant_name": (
            receipt.merchant_name.value
            if receipt.merchant_name and receipt.merchant_name.value is not None
            else None
        ),
        "transaction_date": (
            receipt.transaction_date.value.isoformat()
            if receipt.transaction_date and receipt.transaction_date.value is not None
            else None
        ),
        "receipt_type": (
            receipt.receipt_type.value
            if receipt.receipt_type and receipt.receipt_type.value is not None
            else None
        ),
        "currency": receipt.currency,
        "subtotal": (
            str(receipt.subtotal.value.amount)
            if receipt.subtotal and receipt.subtotal.value is not None
            else None
        ),
        "total_tax": (
            str(receipt.total_tax.value.amount)
            if receipt.total_tax and receipt.total_tax.value is not None
            else None
        ),
        "total": (
            str(receipt.total.value.amount)
            if receipt.total and receipt.total.value is not None
            else None
        ),
        "item_count": len(receipt.items),
    }
    print(json.dumps(mapped, indent=2))
    print("manifest comparison:")
    for key, expected_value in expected.items():
        actual = mapped.get(key)
        print(f"  {key}: expected={expected_value!r} mapped={actual!r}")


def main() -> None:
    service = DocumentIntelligenceService()

    happy_result = service.analyze_invoice(INVOICE_HAPPY_PATH)
    if not happy_result.documents:
        raise RuntimeError("Happy-path invoice returned no documents.")
    happy_invoice = Invoice.from_document_intelligence(happy_result.documents[0].as_dict())
    summarize_invoice(
        "invoice 01-en-happy-classic",
        happy_invoice,
        {
            "vendor_name": "Bright Spark Europe S.A.S.",
            "vendor_vat_id": "FR61954506077",
            "customer_name": "Northstar Facilities B.V.",
            "customer_vat_id": "NL00449544B01",
            "invoice_number": "EN-2026-1001",
            "invoice_date": "2026-07-01",
            "due_date": "2026-07-31",
            "purchase_order": "PO-4001",
            "currency": "EUR",
            "subtotal": "100.0",
            "total_tax": "21.0",
            "invoice_total": "121.0",
        },
    )
    print("\nfull invoice model:")
    dump_model(happy_invoice)

    missing_vat_result = service.analyze_invoice(INVOICE_MISSING_VENDOR_VAT)
    if not missing_vat_result.documents:
        raise RuntimeError("Missing-VAT invoice returned no documents.")
    missing_vat_invoice = Invoice.from_document_intelligence(
        missing_vat_result.documents[0].as_dict()
    )
    summarize_invoice(
        "invoice 05-nl-missing-vendor-vat",
        missing_vat_invoice,
        {
            "vendor_name": "Groen Onderhoud B.V.",
            "vendor_vat_id": None,
            "invoice_number": "NL-2026-5005",
            "purchase_order": "PO-4005",
            "invoice_total": "387.2",
        },
    )

    receipt_result = service.analyze_receipt(FUEL_RECEIPT)
    if not receipt_result.documents:
        raise RuntimeError("Fuel receipt returned no documents.")
    receipt = Receipt.from_document_intelligence(receipt_result.documents[0].as_dict())
    summarize_receipt(
        "receipt 13-nl-fuel-receipt",
        receipt,
        {
            "merchant_name": "North Sea Fuel B.V.",
            "transaction_date": "2026-07-19",
            "currency": "EUR",
            "subtotal": "50.0",
            "total_tax": "10.5",
            "total": "60.5",
        },
    )
    print("\nfull receipt model:")
    dump_model(receipt)


if __name__ == "__main__":
    main()
