# AIVOA.AI architecture and implementation guide

## 1. Purpose and scope

AIVOA.AI is a full-stack pharmaceutical customer-complaint management application. It supports the early QMS complaint lifecycle: receiving a narrative or supported document, extracting intake facts, making an initial risk recommendation, checking for likely duplicates, collecting human QA review, storing the complaint, and reporting operational analytics.

The application is an **AI-assisted intake tool**, not an autonomous quality or regulatory decision system. Risk, root-cause, CAPA, and duplicate outputs are recommendations. Qualified QA personnel remain responsible for review, investigation, disposition, and regulatory decisions.

## 2. System at a glance

```text
                         Browser
                            |
                            v
  React + Vite + Redux Toolkit (served by Nginx in Docker)
      Dashboard | Complaints | Log Complaint | Analytics | Settings
                            |
                       HTTPS / REST
                            |
                            v
                    FastAPI application
       API routes | validation | document extraction | persistence
             |                         |                    |
             |                         |                    +--> PostgreSQL
             |                         |                      complaints
             |                         |                      analysis_records
             |                         |                      audit_logs
             |                         v
             |                  Typed LangGraph workflow
             |                         |
             |                  provider abstraction
             |                    /                    \
             v                   v                      v
        local parsing       Gemini 3.7 Flash       Gemini 2.5 Flash
          fallback             (primary)              (fallback)
```

The Docker deployment consists of three services:

| Service | Responsibility | Exposed port |
| --- | --- | --- |
| `frontend` | Builds the React single-page app and serves it through Nginx. | `5173` on host -> `80` in container |
| `backend` | Runs FastAPI, applies Alembic migrations at startup, executes complaint workflows, and accesses the database. | `8000` |
| `db` | PostgreSQL 16 persistent store. | Internal to Compose |

The `postgres_data` named Docker volume retains database data across container recreation.

## 3. Frontend architecture

The frontend is a React 18 single-page application built with Vite. `react-router-dom` provides the application routes, Redux Toolkit stores intake and collection state, and Recharts renders dashboard and analytics charts. Nginx uses an SPA fallback (`try_files ... /index.html`) so client-side routes work when opened directly.

### Screens and responsibilities

| Route | Component | What it does |
| --- | --- | --- |
| `/` | `Dashboard` | Shows KPI counts, severity distribution, recent complaints, and daily status trend. |
| `/complaints` | `Complaints` | Loads and filters persisted complaints in the browser. |
| `/log` | `LogComplaint` | Main assisted-intake workspace: chat/document input, populated ledger, review, duplicate gate, and save. |
| `/analytics` | `Analytics` | Uses aggregated backend data for volume, severity, status, source, customer, product, and complaint-type trends. |
| `/settings` | `Settings` | Shows non-secret runtime configuration and can delete all business data after browser confirmation. |

### State and API boundary

`frontend/src/services/api.js` is the single HTTP client boundary. Its base URL is injected at build time through `VITE_API_BASE_URL`; no API address is hard-coded in components. It turns non-success responses into useful error messages and uses `FormData` for document upload.

The Redux store contains three slices:

- `complaint`: the editable intake form, most recent AI analysis, loading state, and errors;
- `complaints`: the persisted complaint list; and
- `dashboard`: summary statistics.

Async thunks call the API for intake, saving, listing, and dashboard data. When intake completes, the returned `extracted_complaint` is merged into the form. The UI keeps the user in control: it displays suggested values and only persists them after the user passes the required-field and duplicate checks and selects Save.

### Intake user journey

1. The QA user pastes a complaint/email, enters a correction in natural language, or attaches PDF, DOCX, TXT, or EML.
2. For an attachment, the client first calls document extraction, then submits the extracted plain text to intake with `source_type: "document"`.
3. The client calls `POST /api/complaints/intake`, passing raw text and the current form values. The latter gives the workflow context and avoids erasing fields already reviewed.
4. The workflow response populates the ledger, confidence data, completeness result, risk recommendation, root-cause/CAPA suggestions, duplicate result, stage list, and conversational summary.
5. Before save, the UI requires its configured operational fields (source, customer, product, strength/grade, batch/lot, quantity, manufacturing/expiry values, category, and description). Missing values can be entered directly or supplied through another Copilot message.
6. The client calls `POST /api/complaints/duplicate-check`. A potential match stops automatic save and asks the user to decide; it never silently merges records.
7. If no match blocks the action, the client calls `POST /api/complaints`; the backend assigns an ID/complaint number and writes the record and audit entry. The dashboard and complaint list are then refreshed.

## 4. Backend architecture

The backend is a Python FastAPI application. `app.main` configures CORS, creates the SQLAlchemy metadata for a clean startup, makes a narrow compatibility addition for older `complaints` tables, mounts the REST router under `/api`, and exposes `/health`.

The main backend layers are:

```text
HTTP route
  -> Pydantic request/response schema validation
  -> domain helper / LangGraph invocation
  -> SQLAlchemy session and ORM model (when data is persisted)
  -> PostgreSQL
```

- `app/api/routes.py` contains HTTP endpoints and the deterministic duplicate-comparison helper.
- `app/schemas/` defines Pydantic payload contracts. Complaint date-like values are intentionally strings so customer-supplied, uncertain values can be preserved rather than rejected or guessed.
- `app/ai/graph/workflow.py` defines the typed LangGraph state and pipeline.
- `app/ai/providers/` isolates provider-specific LangChain calls behind `BaseLLMProvider`.
- `app/documents/extractor.py` extracts text from supported uploads.
- `app/models/` defines SQLAlchemy entities; `app/db/` owns the declarative base, engine, and request-scoped sessions.

### REST API

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Basic service health response. |
| `POST /api/complaints` | Create a reviewed complaint and an audit log entry. If absent, `received_date` is set to intake date. |
| `GET /api/complaints` | List complaints; supports optional `status` and `q` server filters. |
| `GET /api/complaints/{id}` | Fetch one complaint. |
| `PUT /api/complaints/{id}` | Update supplied complaint fields and add an audit log entry. |
| `DELETE /api/complaints/{id}` | Delete one complaint. |
| `POST /api/complaints/intake` | Run the LangGraph intake pipeline without saving. |
| `POST /api/complaints/duplicate-check` | Check an unsaved form against persisted complaints. |
| `POST /api/complaints/{id}/analyze` | Run full analysis for a saved complaint, persist its result, and update stored severity, priority, and risk level. |
| `POST /api/complaints/{id}/risk-assessment`, `/duplicate-check`, `/root-cause`, `/capa`, `/summary` | Run and store the requested portion of a saved complaint’s analysis. |
| `POST /api/documents/extract` | Extract plain text from PDF, DOCX, TXT, or EML content. |
| `POST /api/ai/copilot` | Provides a small deterministic, human-review-labelled answer for common Copilot questions. |
| `GET /api/dashboard/statistics` | Dashboard totals, grouped severity/status values, and recent complaints. |
| `GET /api/dashboard/analytics` | Chart-ready complaint aggregates. |
| `GET /api/settings/info` | Non-secret configuration and provider availability. It never returns API keys. |
| `DELETE /api/settings/data` | Permanently deletes complaint, analysis, and audit data while preserving schema/configuration. |

## 5. LangGraph AI workflow

`complaint_graph` is compiled once when the backend imports `workflow.py`. It uses a `TypedDict` state (`ComplaintState`) and a fixed sequential graph; there are no conditional branches or background agents in the current implementation.

```text
START
  -> classify
  -> extract
  -> normalize
  -> completeness
  -> risk
  -> duplicates
  -> root_cause
  -> capa
  -> summary
  -> END
```

| Node | Responsibility | Important behavior |
| --- | --- | --- |
| `classify` | Records that input was classified. | Adds a stage marker; it does not currently route input differently. |
| `extract` | Produces named complaint fields. | First recognizes short explicit field changes; otherwise uses an LLM when configured; falls back to local regex extraction if unavailable/failing. |
| `normalize` | Merges extracted values with the existing form. | Ignores null updates and protects an existing description from being replaced by a substantially shorter one. |
| `completeness` | Assesses four core fields. | Core fields are customer, product, batch, and description. It returns missing-field questions and a confidence score. |
| `risk` | Makes a deterministic initial risk recommendation. | Critical keywords include contamination, adverse event, patient injury, foreign particle, and sterility; damage/defect/discoloration gives Medium absent higher triggers. |
| `duplicates` | Adds workflow duplicate candidates. | Currently returns an empty list; the persisted-data duplicate check happens in the API layer. |
| `root_cause` | Returns an investigation starting point. | Suggests packaging/transit investigation for blister, damaged, or broken complaints; otherwise a product-quality investigation area. |
| `capa` | Returns generic corrective and preventive starting recommendations. | Examples: inspect/quarantine retained samples, open a batch investigation, and review relevant SOP/process controls. |
| `summary` | Builds the response sent to the UI. | Adds risk-derived fields to the normalized complaint and returns the full review payload plus stages. |

### Extraction and LLM integration

The only LLM-dependent graph node is extraction. `ExtractionOutput` is a Pydantic schema, and the provider invokes LangChain structured output against it. This makes the LLM return a controlled field shape instead of arbitrary prose.

`BaseLLMProvider` exposes `structured(prompt, schema)`. The selected implementation is determined server-side:

- `LLM_PROVIDER=gemini` with `GEMINI_API_KEY` selects `ChatGoogleGenerativeAI`. It first calls `GEMINI_MODEL` (`gemini-3.7-flash` by default), then retries with `GEMINI_FALLBACK_MODEL` (`gemini-2.5-flash`) using the same key and Gemini API base URL.
- `LLM_PROVIDER=groq` with `GROQ_API_KEY` remains available as an optional alternative.
- No valid configured provider, or an extraction exception, selects the local regex fallback. The result explicitly includes `LLM unavailable; used local regex fallback.`

This separation keeps LangGraph business logic independent from either vendor and prevents keys from reaching the browser. The rest of the graph—normalization, completeness, risk, root-cause, CAPA, and summary—is deterministic in this version, which makes outcomes explainable and testable even without credentials.

### Preserving human-provided values

For short messages such as `Change manufacturing date to ...`, the extraction node detects recognised labels and saves everything after the label as entered. It deliberately does not impose a date pattern. This is important for pharmaceutical complaint intake because a source may report an incomplete or unreadable date that QA must investigate rather than silently normalize.

## 6. Document ingestion

The document endpoint accepts bytes and extracts text in memory:

| Extension | Extractor |
| --- | --- |
| `.txt` | UTF-8 decoding with replacement for malformed characters. |
| `.pdf` | PyMuPDF (`fitz`) page text extraction. |
| `.docx` | `python-docx` paragraph text extraction. |
| `.eml` | Python email parser, preferring a plain-text body. |

The extracted text is returned to the browser; it is then processed through the same intake endpoint as pasted text. There is no production OCR, attachment persistence, malware scanning, or image-PDF recognition in the present implementation.

## 7. Data architecture and audit trail

PostgreSQL is the production Compose database. A local SQLite URL is the code default, which makes simple local development possible. SQLAlchemy uses UUID strings as primary keys.

| Table | Contents |
| --- | --- |
| `complaints` | Complaint identity/number, workflow status, source/customer/product/batch details, free-form date-like values, description, impact fields, AI-assisted severity/priority/risk/action, and timestamps. |
| `analysis_records` | JSON payloads from full or individual saved-complaint analyses, analysis type, provider marker (`langgraph`), and timestamp. |
| `audit_logs` | Complaint-linked activity (`Complaint created`, `Complaint updated`, `AI analysis completed`) with JSON details and timestamp. |

Complaint numbers use the `CC-YYYYMMDD-microseconds` pattern. New records default to `PENDING_REVIEW`. The code supports updates and logs them; it does not technically make records immutable. The bulk data-deletion settings endpoint is intentionally destructive and should be restricted or removed in a production deployment.

### Duplicate detection

The API compares an incoming complaint against all persisted complaints after lowercasing and punctuation-normalizing values. It weights exact/similar signals as follows: batch 35%, product 20%, type 15%, customer 10%, description 15%, and affected quantity 5%.

A candidate must have a meaningful anchor—an identical batch, or closely matching product plus type/description—and a score of at least `0.55`. It returns a score and human-readable reasons, but never deduplicates automatically. The API-layer checker is what the save workflow uses; the LangGraph `duplicates` node is presently a transparent placeholder.

## 8. Schema migrations and startup behavior

Alembic manages the database evolution:

1. `001_initial` creates the three tables and indexes while safely tolerating tables from an older startup-created installation.
2. `002_copilot_intake_fields` adds originating-site, impacted-materials, suggested-action, and initial-risk fields.
3. `003_preserve_intake_values` changes manufacturing, expiry, complaint, and received date fields from SQL dates to text. Its downgrade intentionally raises an error because arbitrary free-form values cannot safely be converted back without QA review.

The backend Docker command runs `alembic upgrade head` before Uvicorn starts. `Base.metadata.create_all()` at startup also supports clean installs; production change management should still use Alembic as the authoritative migration path.

## 9. Configuration and deployment

All environment-specific values are configuration, not source code:

| Variable | Meaning |
| --- | --- |
| `VITE_API_BASE_URL` | API base URL baked into the frontend build, normally `http://localhost:8000/api`. |
| `DATABASE_URL` | SQLAlchemy connection URL. Compose uses the internal `db` hostname. |
| `FRONTEND_ORIGIN` | Allowed frontend origin used by CORS configuration. |
| `LLM_PROVIDER` | `gemini` (default) or `groq`. |
| `GROQ_API_KEY`, `GROQ_MODEL` | Groq credentials/model; default model is `llama-3.1-8b-instant`. |
| `GEMINI_API_KEY` | Shared Gemini credential for both models. |
| `GEMINI_MODEL`, `GEMINI_FALLBACK_MODEL` | Primary `gemini-3.7-flash` and fallback `gemini-2.5-flash`. |
| `GEMINI_BASE_URL` | Gemini API host; defaults to `https://generativelanguage.googleapis.com`. |

For Docker development, copy `.env.example` to `.env` and run `docker compose up --build`. Open the web application at `http://localhost:5173`, FastAPI interactive documentation at `http://localhost:8000/docs`, and health status at `http://localhost:8000/health`.

For local development, run the backend with `uvicorn app.main:app --reload` after installing `backend/requirements.txt` and applying `alembic upgrade head`; run the frontend with `npm install` and `npm run dev` from `frontend`.

## 10. Verification and development practices

Backend tests in `backend/tests/test_graph.py` verify the deterministic workflow’s Medium damaged-packaging outcome, Critical safety trigger, field-value preservation, and free-form intake values. Run them from `backend` with `pytest`.

Useful checks during development:

```bash
# Backend
cd backend
pytest
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm test
npm run build
```

## 11. Current limitations and production considerations

- AI extraction depends on external provider availability when keys are configured; regex fallback has lower fidelity and reports that it was used.
- Risk, root-cause, and CAPA logic is deliberately initial and rule-based outside extraction. It is not a validated risk engine or investigation decision.
- PDF extraction is text-only; scanned documents need OCR before intake.
- The frontend complaint search is client-side after a full list load. The API has only basic `status` and text query filtering.
- The API currently has CORS but no authentication, authorization, tenant isolation, rate limiting, request-size policy, or role-based control. These are necessary before handling real regulated or personal data.
- Audit entries exist for create/update/full analysis, but audit controls, immutable history, electronic signatures, retention, backup/restore, validation evidence, and regulatory controls would need to be designed for a production GxP deployment.
- The data-clear endpoint is appropriate for a demo environment only unless protected by strong administrative authorization and retention policy.

## 12. Source map

| Area | Primary files |
| --- | --- |
| Application entry point/CORS | `backend/app/main.py` |
| HTTP endpoints and duplicate scoring | `backend/app/api/routes.py` |
| LangGraph workflow | `backend/app/ai/graph/workflow.py` |
| Provider abstraction | `backend/app/ai/providers/base.py`, `backend/app/ai/providers/factory.py` |
| Prompts and structured output | `backend/app/ai/prompts/`, `backend/app/schemas/ai.py` |
| ORM entities | `backend/app/models/complaint.py` |
| API schemas | `backend/app/schemas/complaint.py` |
| Document extraction | `backend/app/documents/extractor.py` |
| React routes/views | `frontend/src/App.jsx`, `frontend/src/pages/` |
| API client and Redux state | `frontend/src/services/api.js`, `frontend/src/store/index.js` |
| Containers | `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile` |
| Migrations/tests | `backend/alembic/versions/`, `backend/tests/test_graph.py` |
