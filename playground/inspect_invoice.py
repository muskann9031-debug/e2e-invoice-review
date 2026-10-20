"""Run the Document Intelligence surface against a sample invoice."""
# %%
from __future__ import annotations

import json
import sys
from pathlib import Path

from azure.ai.documentintelligence.models import AnalyzeResult

from pathlib import Path

REPO_ROOT = Path(r"C:\Users\muska\OneDrive\Documents\e2e-invoice-review")
PLAYGROUND_DIR = REPO_ROOT / "playground"
BACKEND_DIR = REPO_ROOT / "backend"
SAMPLE_INVOICE_PATH = REPO_ROOT / "samples" / "generated" / "01-en-happy-classic.pdf"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.document_intelligent_services import (  # noqa: E402
    PREBUILT_INVOICE_MODEL,
    DocumentIntelligenceService,
)


def print_invoice_data_model(result: AnalyzeResult) -> None:
    print(f"result_type={type(result).__name__}")
    print(f"model_id={result.model_id}")
    print(f"api_version={result.api_version}")
    print(f"page_count={len(result.pages or [])}")
    print(f"document_count={len(result.documents or [])}")
    print()

    if not result.documents:
        print("No documents were returned.")
        return

    for index, document in enumerate(result.documents):
        print(f"--- document[{index}] {type(document).__name__} ---")
        print(f"doc_type={document.doc_type}")
        print(f"confidence={document.confidence}")
        print(json.dumps(document.as_dict(), indent=2, default=str))


def main() -> None:
    service = DocumentIntelligenceService()
    print(f"Analyzing {SAMPLE_INVOICE_PATH} with {PREBUILT_INVOICE_MODEL}")
    result = service.analyze_invoice(SAMPLE_INVOICE_PATH)
    print_invoice_data_model(result)


if __name__ == "__main__":
    main()

# %%

