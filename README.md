# AI Invoice Review

An end-to-end invoice and receipt review application for a fictional European
business. It combines Azure document extraction and AI-assisted review with
deterministic finance checks, SQLite persistence, and a human approval workflow.

## The problem

Finance teams receive invoices and expense receipts in different formats and
languages. Before recording them, reviewers need to confirm extracted values,
check totals and VAT, and select an accounting category. This project turns that
work into a single upload-to-review flow while keeping policy decisions and final
approval under human control.

## Implemented features

- Upload a PDF, JPEG, or PNG, with a 4 MB file-size limit.
- Classify a document as an invoice, receipt, or unsupported document using
  structured Azure OpenAI output. Unsupported documents are stopped before
  Document Intelligence extraction.
- Extract invoices and receipts with the corresponding Azure AI Document
  Intelligence prebuilt model.
- Retain receipt payment method/amount and country/region evidence when those
  fields are present in extraction output.
- Retain extracted values alongside the source OCR content and confidence where
  Document Intelligence provides them.
- Independently review the original document with Azure OpenAI; keep
  Document Intelligence values primary and fill only missing fields from the
  review, with provenance and conflicts exposed.
- Apply deterministic invoice and receipt validation, including local EU VAT
  structure/checksum checks, receipt total reconciliation, duplicate detection,
  and confidence warnings.
- Suggest an account from a fixed general-ledger catalog; a reviewer can change
  the selection.
- Review, correct, approve, or reject documents in the React interface, with
  SQLite-backed history and deletion.
- Draft a supplier correction email on demand. The application does not send
  email.
- Run the frontend and FastAPI backend locally or build a single-container
  Docker image.

The fictional client and supplier corpus is for demonstration. VAT checks are
local format/checksum validation; the application does not query VIES. The model
suggestion does not replace deterministic policy or reviewer approval.

## Technology

- **Backend:** Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, SQLite, uv
- **Document extraction:** Azure AI Document Intelligence
- **Classification and review:** Azure OpenAI; Pydantic AI structured output for
  classification and GL suggestions
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, pnpm
- **Packaging:** Docker

## Architecture and workflow

```text
React UI
  -> FastAPI upload API
  -> Azure OpenAI classification
  -> Azure Document Intelligence invoice/receipt extraction
  -> Azure OpenAI independent review and deterministic field merge
  -> local finance validation and GL suggestion
  -> SQLite persistence
  -> human correction, review, and approval
```

HTTP handling, orchestration, persistence, provider adapters, and deterministic
business rules are separated in the backend. The Azure SDK boundary is kept in
the provider/service layer; normalized extraction schemas retain evidence for
review. Environment configuration is centralized in
[`backend/app/config.py`](backend/app/config.py) and
[`frontend/src/lib/env.ts`](frontend/src/lib/env.ts).

## Requirements

- Python 3.12 or newer and [uv](https://docs.astral.sh/uv/)
- Node.js 22 or newer and pnpm 11
- Azure AI Document Intelligence and Azure OpenAI resources for live document
  processing
- Docker (optional)

## Local setup

Copy the environment templates, then add your own Azure resource values to the
local backend `.env` file. Do not commit `.env` files or credentials.

PowerShell:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

Install the locked dependencies:

```powershell
Set-Location backend
uv sync --locked

Set-Location ..\frontend
pnpm install --frozen-lockfile
```

Start the backend and frontend in separate terminals:

```powershell
Set-Location backend
uv run --locked --no-sync uvicorn app.main:create_app --factory --reload
```

```powershell
Set-Location frontend
pnpm dev
```

Open the Vite URL (normally `http://localhost:5173`). The API health endpoint
is `http://localhost:8000/health`. Azure settings are required to start the
backend; uploading a document invokes configured Azure services and may incur
usage charges. No Azure requests are made by the local lint, type-check, or
build commands.

## Environment variables

Set these in `backend/.env` (the checked-in example contains placeholders only):

| Variable | Purpose |
| --- | --- |
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | Document Intelligence resource endpoint |
| `AZURE_DOCUMENT_INTELLIGENCE_KEY` | Document Intelligence key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `AZURE_OPENAI_DEPLOYMENT` | Azure deployment name; defaults to `gpt-6-astra` and can be overridden |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key |
| `ALLOWED_ORIGIN` | Allowed frontend origin; defaults to `http://localhost:5173` |
| `APP_ACCESS_PASSWORD` | Optional shared-password gate |
| `APP_SESSION_SECRET` | Required when the password gate is enabled |

The frontend template uses `VITE_API_BASE_URL=http://localhost:8000` for local
development. The Docker image builds the frontend to use the same-origin API.

## Demo

Add screenshots or a short walkthrough recording here after capturing the final
application flow.

## Limitations and next steps

- Processing requires configured Azure services and depends on model output;
  no cloud behavior is claimed as verified by local build checks.
- Each request handles one document, with a 4 MB limit.
- VAT validation is offline; there is no VIES registration lookup.
- GL accounts are a fixed local catalog; there is no accounting-system
  integration.
- Correction emails are drafts only; the app does not send them.
- SQLite and local file storage are suitable for this demonstration, not a
  multi-user production deployment.

Potential next improvements include a browser walkthrough with fictional
documents, richer review provenance display, and deployment documentation for
securely managed production secrets and persistent storage.

## Acknowledgment

This project is inspired by the
[Data Lumina invoice-review tutorial](https://learn.datalumina.com/docs/invoice-review)
and its original
[tutorial repository](https://github.com/daveebbelaar/e2e-invoice-review).
The implementation in this repository extends that teaching foundation with
the application workflow and integrations described above.
