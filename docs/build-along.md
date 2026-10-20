# Build-along guide

The complete guided build lives at <https://learn.datalumina.com/docs/invoice-review>. This local guide records the first checkpoint represented by the `main` branch.

## Starter outcome

The repository installs reproducibly, starts a minimal FastAPI service and React interface, and includes the business brief plus fictional source documents.

## Why this boundary exists

The starter removes the completed workflow while preserving every prerequisite needed to build it. You begin with the user, the source documents, and explicit service boundaries instead of reverse-engineering a finished application.

## Commands

```bash
cd backend
uv sync --locked

cd ../frontend
pnpm install --frozen-lockfile

cd ..
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
./scripts/dev.sh --check
./scripts/dev.sh
```

## Important locations

- `docs/client-brief.md`: the recurring finance problem and definition of done
- `docs/architecture.md`: the intended boundaries and data flow
- `samples/`: the fictional evaluation corpus and manifest
- `backend/app/main.py`: the initial API boundary
- `frontend/src/App.tsx`: the initial interface boundary

## What you should observe

- `GET http://localhost:8000/health` returns `{"status":"ok"}`.
- `http://localhost:5173` shows the Invoice Review starter screen.
- No Azure request occurs at this checkpoint.

## Checkpoint

- [ ] Locked backend and frontend installs succeed.
- [ ] Backend lint passes.
- [ ] Frontend type-check, lint, and production build pass.
- [ ] `./scripts/dev.sh --check` reports that Invoice Review is ready to start.
- [ ] The health endpoint and starter screen load locally.

Continue with the [online tutorial](https://learn.datalumina.com/docs/invoice-review).

## Azure OpenAI provider surface

The backend now has a small provider adapter for text generation through Azure
OpenAI's Responses API. It reads `AZURE_OPENAI_ENDPOINT` and
`AZURE_OPENAI_API_KEY` from the backend environment or `backend/.env`. The
deployment identifier (`gpt-6-astra`) is fixed in the adapter, so no key or
endpoint belongs in source code.

### Why this boundary exists

The adapter keeps the OpenAI SDK client and response types inside
`backend/app/providers/azure_openai.py`, while callers receive plain text.
Both Azure providers share `backend/app/config.py` for environment loading.

### Commands

```bash
cd backend
uv run --locked --no-sync ruff check app test.py
uv run --locked --no-sync python test.py
```

The second command sends one billable request to Azure OpenAI and requires
`AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` to be set in `backend/.env`
or the process environment.

### What you should observe

- Ruff reports no issues.
- The smoke check prints an `answer:` line from the configured model.
- Missing endpoint or key produces a clear configuration error before a request.

### Checkpoint

- [ ] The provider reads endpoint and key from environment configuration.
- [ ] The model is selected from the fixed `gpt-6-astra` identifier.
- [ ] The smoke check returns plain text without exposing provider SDK types.

## Preserving Document Intelligence evidence

The shared parser keeps OCR content and confidence when Azure does not provide
a typed date, number, or currency amount. In that case, `ExtractedValue.value`
is `None`; successfully parsed values keep their existing types. Malformed
array entries are reported by field and index, then skipped without logging
document content.

### Why this boundary exists

Keeping raw evidence available gives later AI review enough context to assess
unparsed primary extraction without pretending the OCR text is a validated
date or amount. The parser stays shared; invoice and receipt schemas still own
their document-specific mappings.

### Commands

```bash
cd backend
uv run --locked --no-sync ruff check --ignore I001 app/schemas/common.py app/schemas/document_fields.py app/schemas/receipt/model.py ../playground/map_schemas.py
uv run --locked --no-sync python -c "from app.schemas.document_fields import extracted_date; field=extracted_date({'Date': {'content': '31/12/2025', 'confidence': 0.42}}, 'Date'); assert field is not None and field.value is None and field.content == '31/12/2025' and field.confidence == 0.42"
uv run --locked --no-sync python -c "from app.schemas.document_fields import object_list; rows=object_list({'Items': {'valueArray': [{'valueObject': {'Description': {'valueString': 'Good'}}}, None, {}]}}, 'Items'); assert len(rows) == 1"
```

The focused Ruff command ignores `I001` because the current workspace already
has import-order findings outside this change.

### What you should observe

- Properly typed values still map with their OCR content and confidence.
- Unparsed fields retain evidence with `value=None`.
- Malformed array rows produce warnings containing only the collection name
  and row index; valid rows continue to map.
- Mock-dictionary checks require no Azure calls.

### Checkpoint

- [ ] Evidence-only values preserve OCR content and confidence.
- [ ] Currency and playground consumers guard nullable values.
- [ ] Malformed collection rows are reported and do not create empty models.

## Structured document classification

The pipeline accepts document bytes and a media type, then uses Pydantic AI
with the configured Azure OpenAI Responses API deployment to return a validated
`DocumentClassification`: `invoice`, `receipt`, or `other`, plus a confidence
score. The pipeline passes PDFs and PNG/JPEG images directly to the model.

### Why this boundary exists

The model classifies the incoming document before extraction, so the caller can
route invoices to `prebuilt-invoice`, receipts to `prebuilt-receipt`, and
`other` documents to neither. Pydantic AI owns structured-output handling; its
OpenAI client and model types remain inside the Azure provider adapter. The
confidence is a model estimate, not a deterministic policy decision.

### Commands

```bash
cd backend
uv sync --locked
uv run --locked --no-sync ruff check app/pipeline/classification.py app/providers/azure_openai.py app/schemas/classification.py
uv run --locked --no-sync python -c "from app.schemas.classification import DocumentClassification; result=DocumentClassification(document_type='invoice', confidence=0.95); assert result.document_type == 'invoice' and result.confidence == 0.95"
```

The local check validates the result schema without contacting Azure. Calling
`classify_document()` makes a billable Azure OpenAI request and requires the
existing `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` settings.

### What you should observe

- The local schema check exits successfully.
- A classification request returns only the validated document type and score.
- Unsupported media types and empty document bytes fail explicitly.

### Checkpoint

- [ ] Pydantic AI returns a provider-independent structured classification.
- [ ] The pipeline can pass through supported PDF, PNG, and JPEG documents.
- [ ] No Azure call is made by the local schema check.
