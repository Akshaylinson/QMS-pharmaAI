You are a senior full-stack AI product engineer.

Build the COMPLETE working project described below.

PROJECT NAME:
AIVOA.AI – AI-Powered Customer Complaint Management System

PROJECT CONTEXT:
This is an AI Product Engineer assignment for AIVOA.AI.

The goal is to build an AI-powered Customer Complaint Management System for the pharmaceutical manufacturing industry, specifically supporting pharmaceutical API and FDF manufacturing complaint workflows.

The system must demonstrate a realistic pharmaceutical Customer Complaint intake and AI-assisted assessment workflow.

The application must be production-quality in architecture and clean enough to be demonstrated during a technical interview.

IMPORTANT:
Do not create a toy chatbot.
Do not create only a frontend mockup.
Do not hard-code AI responses.
Do not bypass LangGraph.
Implement a complete end-to-end workflow:

User complaint input
→ document/text ingestion
→ complaint extraction
→ validation
→ AI analysis
→ complaint form population
→ risk assessment
→ AI recommendations
→ user review/edit
→ database persistence
→ complaint summary/status.

==================================================
1. MANDATORY TECHNOLOGY STACK
==================================================

FRONTEND:
- React
- Redux Toolkit for state management
- React Router
- Google Inter font
- Modern component architecture
- Responsive UI
- White/light professional enterprise design

BACKEND:
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic database migrations

AI ORCHESTRATION:
- LangGraph
- LangChain where appropriate
- Structured LLM outputs
- Typed state between graph nodes

LLM:
The original assignment specifies:
- Groq
- gemma2-9b-it

However, gemma2-9b-it is now deprecated/shut down on Groq.

Therefore DO NOT hard-code the retired model.

Create an LLM provider abstraction.

PRIMARY CURRENT PROVIDER:
- Groq API
- configurable model through environment variable
- default current production-compatible Groq model

Example:
GROQ_MODEL=llama-3.1-8b-instant

SECONDARY PROVIDER:
- Google Gemini API
- configurable through environment variable
- support modern Gemini Flash models

Example:
GEMINI_MODEL=gemini-3.8-flash

The application must allow switching providers through configuration without modifying the LangGraph business logic.

IMPORTANT:
The model must NOT be downloaded into the repository.
The AI models are remote API models.

Use environment variables:

GROQ_API_KEY=
GROQ_MODEL=

GEMINI_API_KEY=
GEMINI_MODEL=

LLM_PROVIDER=groq

The LangGraph workflow must work regardless of the selected provider.

DATABASE:
PostgreSQL

==================================================
2. CORE PRODUCT GOAL
==================================================

Build a pharmaceutical Customer Complaint Management System.

The main screen should resemble a professional QMS complaint-management application.

The primary workflow is:

1. User opens "Log Customer Complaint"
2. User can manually enter information OR upload a complaint document/email/text
3. AI Complaint Intake Assistant processes the input
4. AI extracts relevant complaint information
5. Extracted values populate the complaint form
6. User can review and modify extracted values
7. LangGraph performs complaint analysis
8. System calculates/recommends:
   - severity
   - priority
   - risk
   - complaint completeness
   - potential duplicate
   - possible root cause
   - CAPA recommendation
9. AI Copilot displays assessment
10. User saves the complaint
11. Complaint is persisted in PostgreSQL
12. Complaint receives a unique complaint ID
13. User can later view the complaint and its AI assessment

==================================================
3. UI/UX REQUIREMENTS
==================================================

Design a clean modern enterprise pharmaceutical/QMS interface.

DO NOT copy the screenshot pixel-for-pixel.

Use the screenshot only as workflow inspiration.

Design principles:
- white background
- subtle gray borders
- professional blue accent
- clean cards
- compact enterprise form layout
- excellent typography
- Google Inter
- no excessive gradients
- no unnecessary animations
- no dark UI
- no flashy AI gimmicks
- clear hierarchy
- responsive desktop-first design

Main navigation:

Dashboard
Complaints
Log Complaint
AI Copilot
Analytics
Settings

The main "Log Customer Complaint" page should use a two-column layout.

LEFT:
Complaint form

RIGHT:
AI Complaint Intake Assistant / AI Copilot

==================================================
4. LOG CUSTOMER COMPLAINT FORM
==================================================

Create the following sections.

SECTION 1:
Origin & Customer Details

Fields:
- Complaint Source
- Customer Name
- Customer Organization
- Customer Contact
- Customer Email
- Country / Region

SECTION 2:
Product & Batch Identification

Fields:
- Product Name
- Product Strength / Grade
- Batch / Lot Number
- Manufacturing Date
- Expiry Date
- Product Type
- Market / Country

SECTION 3:
Complaint Details

Fields:
- Complaint Type
- Complaint Date
- Complaint Received Date
- Detailed Complaint Description
- Product Condition
- Quantity Affected
- Sample Available
- Supporting Documents

SECTION 4:
Initial Assessment & Priority

Fields:
- Initial Severity
- Priority
- Patient / Consumer Impact
- Quality Impact
- Regulatory Impact
- Safety Concern

Every field should support:
- manual editing
- AI extraction
- AI confidence indicator where applicable

==================================================
5. AI COMPLAINT INTAKE ASSISTANT
==================================================

Create a dedicated AI assistant panel.

Allow:

A. Drag and drop file upload

Supported demonstration formats:
- PDF
- DOCX
- TXT
- EML
- plain text

B. Paste complaint text/email

C. Manual prompt

Example:

"Customer ABC reports that Batch B2026-001 of Paracetamol 500mg tablets contains broken tablets and several blister packs are damaged."

The assistant should process the input.

Display:

- Upload status
- Processing status
- Extraction progress
- Extracted fields
- Confidence
- Warnings
- Missing information
- Suggested next action

Example states:

Uploading
↓
Reading complaint
↓
Extracting fields
↓
Validating information
↓
Assessing risk
↓
Checking completeness
↓
Ready for review

==================================================
6. LANGGRAPH ARCHITECTURE
==================================================

LangGraph MUST control the complete AI workflow.

Do NOT implement a collection of unrelated LLM calls.

Create a structured graph.

Suggested state:

ComplaintState

Fields:

- raw_input
- source_type
- extracted_complaint
- extraction_confidence
- missing_fields
- validation_errors
- normalized_complaint
- severity_assessment
- risk_assessment
- completeness_assessment
- duplicate_candidates
- root_cause_recommendations
- capa_recommendations
- complaint_summary
- final_response
- errors

Graph:

START
  ↓
Input Classification
  ↓
Document/Text Extraction
  ↓
Complaint Information Extraction
  ↓
Normalization
  ↓
Completeness Check
  ↓
Risk Assessment
  ↓
Duplicate Detection
  ↓
Root Cause Recommendation
  ↓
CAPA Recommendation
  ↓
Complaint Summary
  ↓
Final Validation
  ↓
END

The graph should be modular.

Every node should:
- have a single responsibility
- accept structured state
- return structured state
- handle errors
- be testable independently

==================================================
7. AI FEATURES
==================================================

IMPLEMENT ALL CORE AI FEATURES.

----------------------------------
A. Complaint Information Extraction
----------------------------------

Extract:

- customer
- organization
- product
- strength
- batch
- manufacturing date
- expiry date
- complaint date
- complaint type
- description
- affected quantity
- patient impact
- safety concern
- regulatory concern
- supporting evidence

Return structured JSON.

Never return arbitrary text when structured output is expected.

----------------------------------
B. Complaint Completeness Checker
----------------------------------

Determine whether enough information exists to process the complaint.

Return:

status:
COMPLETE
PARTIALLY_COMPLETE
INCOMPLETE

missing_fields:
[...]

questions_to_ask:
[...]

confidence:
0-1

----------------------------------
C. AI Risk Classification
----------------------------------

Assess:

- severity
- priority
- patient safety risk
- product quality risk
- regulatory risk

Return:

risk_level:
LOW
MEDIUM
HIGH
CRITICAL

severity:
MINOR
MAJOR
CRITICAL

priority:
LOW
MEDIUM
HIGH
URGENT

Also provide concise reasoning.

IMPORTANT:
AI recommendations must be presented as recommendations.
Do not claim that the AI has made a regulatory decision.

----------------------------------
D. Duplicate Complaint Detection
----------------------------------

Compare the incoming complaint against existing complaints in PostgreSQL.

Use deterministic similarity where practical and AI-assisted semantic comparison where useful.

Compare:

- product
- batch
- complaint type
- customer
- description
- date
- affected issue

Return:

duplicate_status
possible_duplicates
similarity_score
reason

----------------------------------
E. Root Cause Recommendation
----------------------------------

Generate possible root causes based on the complaint.

Examples:

- manufacturing defect
- packaging issue
- transportation damage
- storage condition
- labeling issue
- handling issue
- product quality issue
- unknown

Do not claim the root cause is confirmed.

Use wording such as:

"Potential root cause"
"Recommended investigation area"

----------------------------------
F. CAPA Recommendation
----------------------------------

Generate suggested:

Corrective Actions
Preventive Actions

Examples:

- batch investigation
- retain sample inspection
- packaging line inspection
- supplier review
- SOP review
- operator training
- environmental monitoring
- process review

Clearly label these as AI recommendations.

----------------------------------
G. Complaint Summary
----------------------------------

Generate a concise professional summary containing:

- complaint
- customer
- product
- batch
- issue
- severity
- risk
- recommended next action

==================================================
8. AI COPILOT
==================================================

Create an AI Copilot panel on the complaint screen.

The user should be able to ask questions such as:

"What information is missing?"

"Why was this complaint classified as high risk?"

"What should the investigator check?"

"What could be the possible root cause?"

"Summarize this complaint."

"Suggest CAPA actions."

The Copilot must use the current complaint state as context.

It should NOT hallucinate information not present in the complaint.

If information is unavailable, explicitly say:

"Insufficient information in the complaint."

==================================================
9. DATABASE DESIGN
==================================================

Use PostgreSQL.

Create proper normalized tables.

Minimum tables:

users

complaints

complaint_documents

complaint_extractions

risk_assessments

ai_analysis

duplicate_matches

root_cause_recommendations

capa_recommendations

complaint_events

audit_logs

Suggested complaint fields:

id
complaint_number
status
source
customer_name
customer_organization
customer_email
product_name
product_strength
batch_number
manufacturing_date
expiry_date
complaint_type
complaint_date
received_date
description
affected_quantity
patient_impact
quality_impact
regulatory_impact
safety_concern
severity
priority
risk_level
created_at
updated_at

Use UUID primary keys where appropriate.

Create indexes for:

- complaint_number
- batch_number
- product_name
- customer_name
- complaint_date
- status

==================================================
10. API DESIGN
==================================================

Create REST APIs using FastAPI.

Minimum endpoints:

POST /api/complaints

GET /api/complaints

GET /api/complaints/{id}

PUT /api/complaints/{id}

DELETE /api/complaints/{id}

POST /api/complaints/intake

POST /api/complaints/{id}/analyze

POST /api/complaints/{id}/risk-assessment

POST /api/complaints/{id}/duplicate-check

POST /api/complaints/{id}/root-cause

POST /api/complaints/{id}/capa

POST /api/complaints/{id}/summary

POST /api/ai/copilot

POST /api/documents/extract

GET /api/dashboard/statistics

Create proper Pydantic request/response schemas.

Never expose database models directly as API responses.

==================================================
11. DOCUMENT PROCESSING
==================================================

Production-grade OCR is NOT required.

Use practical lightweight document extraction.

For demonstration:

PDF:
- PyMuPDF / fitz

DOCX:
- python-docx

TXT:
- normal text extraction

EML:
- Python email parser

Images:
- optional OCR support if practical

If extraction fails:
return a clear error.

The assignment explicitly allows creation of realistic pharmaceutical complaint PDFs, emails, or images for demonstration.

Create sample complaint documents.

At minimum create:

1. High-risk complaint
2. Medium-risk complaint
3. Low-risk complaint
4. Incomplete complaint
5. Duplicate/similar complaint

==================================================
12. DASHBOARD
==================================================

Create a professional dashboard.

Show:

Total Complaints
Open Complaints
High Risk
Critical
Pending Review
Resolved

Charts:

Complaints by severity
Complaints by status
Complaints by product
Complaints over time

Recent complaints table.

Use realistic demo data.

==================================================
13. COMPLAINT LIST
==================================================

Create a searchable/filterable complaint list.

Filters:

- status
- severity
- priority
- risk
- product
- batch
- date
- complaint type

Columns:

Complaint ID
Date
Customer
Product
Batch
Complaint Type
Severity
Priority
Risk
Status
Actions

==================================================
14. COMPLAINT DETAIL PAGE
==================================================

Display:

Complaint information
Documents
AI extraction
Risk assessment
Completeness
Duplicate detection
Root cause recommendations
CAPA recommendations
Summary
Audit history

Allow the user to edit complaint information.

==================================================
15. STATE MANAGEMENT
==================================================

Use Redux Toolkit.

Suggested slices:

complaintSlice
aiSlice
dashboardSlice
documentSlice
uiSlice

Do not put everything into local component state.

Use Redux for application-level state.

Handle:

loading
success
error
processing
AI streaming/status if implemented

==================================================
16. ERROR HANDLING
==================================================

Implement proper error handling.

Frontend:
- loading states
- empty states
- validation errors
- API errors
- upload errors
- AI errors

Backend:
- FastAPI exception handlers
- structured errors
- logging
- validation

AI:
- provider failure fallback
- malformed structured output handling
- retry where appropriate
- timeout handling

If the primary LLM provider fails and the secondary provider is configured, allow controlled fallback.

==================================================
17. SECURITY
==================================================

Never hard-code API keys.

Use:

.env

Examples:

DATABASE_URL=
GROQ_API_KEY=
GROQ_MODEL=
GEMINI_API_KEY=
GEMINI_MODEL=
LLM_PROVIDER=

Add:

.env.example

Never commit:

.env

Never expose API keys to React.

All LLM calls must occur from the FastAPI backend.

==================================================
18. PROJECT STRUCTURE
==================================================

Use a professional monorepo structure.

Example:

project-root/

frontend/
  src/
    components/
    pages/
    layouts/
    features/
    store/
    services/
    hooks/
    types/
    utils/
    routes/
    App.jsx
    main.jsx

backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
    ai/
      graph/
      nodes/
      providers/
      prompts/
      parsers/
    documents/
    utils/
    main.py

backend/
  alembic/
  tests/

sample_data/
  complaints/
  documents/

docs/

.env.example

README.md

docker-compose.yml

==================================================
19. DOCKER
==================================================

Create docker-compose configuration for:

PostgreSQL
Backend
Frontend

The AI model itself must NOT run inside Docker.

The application connects to external AI APIs.

Provide:

docker compose up --build

as the main startup command.

==================================================
20. TESTING
==================================================

Create backend tests for:

- complaint creation
- complaint retrieval
- document extraction
- structured AI extraction
- completeness checker
- risk assessment
- duplicate detection
- root cause recommendation
- CAPA recommendation
- complaint summary

Create frontend tests for important UI behavior.

Test the LangGraph nodes independently.

==================================================
21. DEMO DATA
==================================================

Create realistic pharmaceutical complaint examples.

Example:

Customer:
ABC Pharmaceuticals

Product:
Paracetamol Tablets 500 mg

Batch:
PCM-2026-001

Complaint:
Customer reports broken tablets and damaged blister packs.

Create different examples with different severity/risk.

Do not use real patient information.

==================================================
22. AI PROMPT ENGINEERING
==================================================

Create centralized prompts.

Do NOT scatter prompts throughout random source files.

Create:

prompts/
  extraction.py
  completeness.py
  risk.py
  duplicate.py
  root_cause.py
  capa.py
  summary.py
  copilot.py

Prompts must instruct the model to:

- return structured information
- avoid hallucination
- distinguish facts from recommendations
- identify missing information
- avoid inventing pharmaceutical regulatory requirements
- explain reasoning concisely
- use only available complaint information

==================================================
23. STRUCTURED OUTPUT
==================================================

Define Pydantic models for AI output.

Examples:

ComplaintExtraction
CompletenessAssessment
RiskAssessment
DuplicateAssessment
RootCauseRecommendation
CAPARecommendation
ComplaintSummary

Validate all LLM output before storing it.

If validation fails:
- retry with correction prompt
- otherwise return a safe structured error

==================================================
24. IMPORTANT PHARMACEUTICAL DOMAIN BEHAVIOR
==================================================

This is a demonstration QMS-style application.

Do not pretend that the application provides legally binding pharmaceutical regulatory decisions.

AI recommendations must be clearly labeled:

"AI Recommendation"

"Requires Human Review"

The system is assisting a QMS user, not replacing qualified QA/QC personnel.

==================================================
25. UI DETAILS
==================================================

Use:

Google Inter font.

Primary design:
- white background
- blue primary actions
- subtle borders
- rounded cards
- clean tables
- professional icons
- readable typography
- accessible form labels
- good spacing

Main CTA:

"Log Customer Complaint"

AI CTA:

"Analyze Complaint"

Document area:

"Drag & drop complaint document here"

Secondary:

"Paste Complaint Text / Email"

After processing:

"AI Extraction Complete"

Show confidence badges.

Example:

Product Name
Paracetamol 500 mg
AI Extracted
98%

Batch Number
PCM-2026-001
AI Extracted
96%

==================================================
26. AI PROCESSING UI
==================================================

Show a visual workflow:

✓ Document received

✓ Complaint extracted

✓ Information validated

✓ Completeness checked

✓ Risk assessed

✓ Duplicate checked

✓ Recommendations generated

✓ Ready for review

Do not fake progress with arbitrary timers.

The UI should reflect actual backend processing stages where possible.

==================================================
27. AUDITABILITY
==================================================

Store important AI processing events.

Record:

- action
- timestamp
- complaint
- AI operation
- model/provider
- result status

Do not store API keys.

==================================================
28. CONFIGURABLE LLM PROVIDERS
==================================================

Implement:

BaseLLMProvider

GroqProvider

GeminiProvider

The LangGraph nodes should depend on the provider abstraction, not directly on Groq or Gemini.

Example:

provider = get_llm_provider()

Then LangGraph uses:

provider.generate_structured(...)

This allows:

LLM_PROVIDER=groq

or:

LLM_PROVIDER=gemini

without rewriting the application.

==================================================
29. MODEL STRATEGY
==================================================

DEFAULT:

Use the current supported Groq production model configured by:

GROQ_MODEL

For compatibility with the original assignment, document that the assignment specified:

gemma2-9b-it

but that model is no longer available on Groq.

Do NOT attempt to download Gemma 2 locally.

OPTIONAL:

Allow Gemini 3.8 Flash through:

GEMINI_MODEL=gemini-3.8-flash

The application must continue to work with the selected provider.

==================================================
30. README
==================================================

Create an excellent README.

Include:

Project overview
Architecture
Tech stack
Features
LangGraph workflow
Database schema
API documentation
Frontend architecture
Environment setup
LLM configuration
PostgreSQL setup
Docker setup
Testing
Sample data
Demo instructions
Known limitations

Explain clearly:

The LLM is accessed through external APIs.
No local model weights are required.

==================================================
31. DEVELOPMENT PRINCIPLES
==================================================

Write clean, understandable code.

Avoid:
- unnecessary abstraction
- duplicated logic
- giant files
- hard-coded AI responses
- fake backend endpoints
- fake database persistence
- fake AI processing
- frontend-only implementation

Every feature shown in the UI must have a real implementation behind it.

The application should be runnable.

==================================================
32. BUILD ORDER
==================================================

Implement in this order:

PHASE 1
Project scaffolding

PHASE 2
PostgreSQL + SQLAlchemy + Alembic

PHASE 3
FastAPI APIs

PHASE 4
React + Redux frontend

PHASE 5
Complaint form

PHASE 6
Document ingestion

PHASE 7
LLM provider abstraction

PHASE 8
LangGraph extraction workflow

PHASE 9
Completeness analysis

PHASE 10
Risk assessment

PHASE 11
Duplicate detection

PHASE 12
Root cause recommendation

PHASE 13
CAPA recommendation

PHASE 14
Complaint summary

PHASE 15
AI Copilot

PHASE 16
Dashboard

PHASE 17
Testing

PHASE 18
Docker

PHASE 19
Documentation

PHASE 20
Final end-to-end validation

==================================================
33. FINAL ACCEPTANCE CRITERIA
==================================================

The project is complete only when:

1. Frontend runs.
2. Backend runs.
3. PostgreSQL runs.
4. Complaint can be entered manually.
5. Complaint PDF/email/text can be uploaded.
6. Document content is extracted.
7. LangGraph processes the complaint.
8. AI extracts structured complaint information.
9. Form is populated with extracted information.
10. User can edit extracted information.
11. Completeness is checked.
12. Risk is assessed.
13. Duplicate complaints can be detected.
14. Root causes are recommended.
15. CAPA actions are recommended.
16. Complaint summary is generated.
17. AI Copilot works.
18. Complaint can be saved to PostgreSQL.
19. Complaint can be retrieved later.
20. Dashboard displays real database data.
21. Errors are handled properly.
22. API keys are protected.
23. Tests exist.
24. README explains the complete architecture.
25. Docker setup works.
26. The complete workflow can be demonstrated end-to-end.

==================================================
34. MOST IMPORTANT REQUIREMENT
==================================================

Build this as an actual AI Product Engineer assignment.

The interviewer must be able to trace:

React UI
↓
Redux
↓
FastAPI endpoint
↓
LangGraph
↓
LLM provider
↓
Structured AI result
↓
LangGraph state
↓
FastAPI response
↓
Redux state
↓
Complaint form / AI Copilot
↓
PostgreSQL persistence

Every part must be understandable and explainable.

Do not hide the AI logic behind a single opaque function.

Do not bypass LangGraph.

Do not replace PostgreSQL with SQLite.

Do not replace React/Redux with another frontend framework.

Do not replace FastAPI.

Do not put AI API keys in the frontend.

Do not use a local LLM unless explicitly requested later.

Build the complete project now.