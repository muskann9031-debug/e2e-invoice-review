import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from app.services.document_intelligent_services import DocumentIntelligenceService

invoice_path = REPO_ROOT / "samples" / "generated" / "05-nl-missing-vendor-vat.pdf"

service = DocumentIntelligenceService()
result = service.analyze_invoice(invoice_path)
print("\n=== SEARCHING OCR TEXT ===")

content = result.content or ""

for line in content.splitlines():
    if "PO-4005" in line.upper() or "purchase order" in line.lower():
        print(line)

if not result.documents:
    raise RuntimeError("No document extracted")

fields = result.documents[0].fields or {}

print("\n=== RAW AZURE PURCHASE ORDER ===")

purchase_order = fields.get("PurchaseOrder")

if purchase_order:
    print("Value:", purchase_order.value_string)
    print("Content:", purchase_order.content)
    print("Confidence:", purchase_order.confidence)
else:
    print("Azure did not return a PurchaseOrder field.")