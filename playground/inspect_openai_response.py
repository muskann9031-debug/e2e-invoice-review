from __future__ import annotations
import truststore
truststore.inject_into_ssl()

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from app.providers.azure_openai import (  # noqa: E402
    AZURE_OPENAI_MODEL,
    AzureOpenAIService,
)

def main() -> None:
    prompt = "What is the capital of France?"

    service = AzureOpenAIService()
    answer = service.generate_text(prompt)

    print(f"Model: {AZURE_OPENAI_MODEL}")
    print(f"Prompt: {prompt}")
    print("\n--- MODEL ANSWER ---")
    print(answer)
    print("\n--- ANSWER AS JSON ---")
    print(json.dumps({"output_text": answer}, indent=2))


if __name__ == "__main__":
    main()