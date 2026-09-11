# AIVOA.AI — Pharmaceutical Complaint Management

A full-stack QMS-style customer complaint intake system for pharmaceutical API/FDF workflows. It ingests complaint text or documents, runs a typed LangGraph assessment, lets a QA user review the populated form, and persists approved intake records in PostgreSQL.

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

The copy step is optional for a local, credential-free demonstration. Open `http://localhost:5173`; API documentation is at `http://localhost:8000/docs`. The stack is three containers: React/Nginx frontend, FastAPI backend, and PostgreSQL.

## Configuration

All deploy-specific values are environment variables; no frontend or backend base URL is hard-coded. See [.env.example](.env.example).

- `VITE_API_BASE_URL` is injected into the frontend build.
- `DATABASE_URL` points the backend at PostgreSQL.
- `LLM_PROVIDER=gemini|groq` selects the provider; Gemini is the default.
- `GEMINI_API_KEY` is shared by `GEMINI_MODEL` (primary `gemini-3.7-flash`) and `GEMINI_FALLBACK_MODEL` (`gemini-2.5-flash`). `GEMINI_BASE_URL` defaults to Google's Gemini API host.
- `GROQ_API_KEY`, `GROQ_MODEL`, and the Gemini settings stay server-side.

Models are always remote APIs—no model weights are downloaded or run in Docker. Without credentials, intake remains demonstrable using a clearly labelled local parsing fallback, and every risk output remains an AI-assistance recommendation requiring human QA review.

## Architecture

```text
React + Redux Toolkit → FastAPI REST API → LangGraph workflow → configured Groq/Gemini API
                              ↘ PostgreSQL (complaints, analysis records, audit logs)
```

The LangGraph workflow is deliberately sequential and typed: input classification → fact extraction → normalization → completeness → risk → duplicate check → root-cause recommendations → CAPA recommendations → summary. Provider calls are behind `BaseLLMProvider`, so graph business logic does not depend on Groq or Gemini.

## Product features

- Editable two-column complaint form and AI Copilot panel.
- PDF, DOCX, TXT, and EML text extraction.
- Field confidence, missing-field questions, risk recommendation, CAPA/root-cause suggestions, and workflow status.
- PostgreSQL complaint CRUD, dashboard statistics, search, auditable analysis records, and UUID primary keys.
- Core REST endpoints under `/api`: complaints CRUD, intake, analysis operations, document extraction, copilot, and dashboard statistics.
- Realistic sample inputs in [sample_data/complaints](sample_data/complaints).

## Development

Backend:

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
pytest
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The initial Alembic revision is in `backend/alembic/versions`; the Docker backend applies migrations automatically on startup. Run `alembic upgrade head` before starting the API locally, especially when upgrading an existing database.

## Known demonstration limits

Document extraction is text-based (no production OCR), duplicate matching is currently a transparent placeholder for persisted-data matching, and QMS recommendations are not regulatory decisions. Review and approval by qualified personnel are mandatory.
