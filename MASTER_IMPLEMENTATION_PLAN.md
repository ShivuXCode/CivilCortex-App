# CivilCortex — Master Implementation Plan

## Purpose

This document is the authoritative implementation roadmap for taking ownership of the existing CivilCortex repository and transforming it from a disconnected prototype into a functioning end-to-end structural inspection and engineering decision-support platform.

This document must be treated as the **primary execution plan** by any AI coding agent or developer working on the repository.

The existing `PROJECT_ANALYSIS.md` is the **discovery/audit document**.

This document is the **implementation document**.

---

# 1. PRODUCT DEFINITION

## 1.1 What CivilCortex Is

CivilCortex is intended to be a structural health assessment platform that allows field inspectors to record structural defects, upload inspection images, automatically analyze those images, assess risk, retrieve relevant engineering standards, and generate an executive maintenance recommendation for review by a qualified engineer.

The intended users are:

* Field Inspectors
* Civil / Structural Engineers
* Lead Engineers
* Infrastructure / Building Maintenance Stakeholders

The core product value is not simply "detect a crack."

The core value is:

> **Convert field evidence into a structured, explainable, standards-backed engineering assessment that helps a qualified engineer make a faster decision.**

---

# 2. CURRENT STATE

The repository currently contains three major conceptual systems:

```text
A. Web Application
   React + FastAPI + SQLAlchemy

B. Computer Vision
   Keras model + MLService

C. Agentic Engineering Analysis
   LangGraph + ChromaDB + Gemini
```

The major problem is that these systems are not connected.

The current web workflow reaches the mocked ML service rather than the actual AI pipeline.

The LangGraph system is primarily exercised through standalone CLI scripts.

The frontend also has no completed workflow for displaying the generated executive report.

Therefore:

> The first objective is NOT to redesign the entire project.

The first objective is to **connect the existing capabilities into one coherent product pipeline**.

---

# 3. TARGET END-TO-END SYSTEM

The target system should eventually follow this architecture:

```text
                    ┌─────────────────────┐
                    │      Inspector      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    React Frontend   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
                    Create Analysis Job
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Async Job Layer   │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┴─────────────────┐
             │                                   │
             ▼                                   ▼
   ┌─────────────────────┐             ┌─────────────────────┐
   │   Computer Vision   │             │    LangGraph        │
   │   Defect Detection  │             │   Agent Workflow    │
   └──────────┬──────────┘             └──────────┬──────────┘
              │                                   │
              │ defect information               │
              └────────────────┬──────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Risk / Assessment   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    ChromaDB RAG     │
                    │ Engineering Codes   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Gemini Synthesis  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Structured Report   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ PostgreSQL Database │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Engineer Review UI  │
                    └─────────────────────┘
```

This is the target architecture.

Do not assume every implementation detail in this diagram must be implemented exactly as shown. Inspect the existing repository and choose the smallest architecture that reliably achieves the same end-to-end behavior.

---

# 4. GUIDING PRINCIPLES

All implementation must follow these principles.

## 4.1 Preserve good existing work

Do not rewrite working functionality unnecessarily.

Especially preserve and reuse:

* Existing FastAPI structure
* Existing SQLAlchemy models where appropriate
* Existing authentication
* Existing React application structure
* Existing LangGraph nodes
* Existing ChromaDB RAG logic
* Existing project hierarchy

The LangGraph nodes should not be rewritten merely for stylistic reasons.

The audit indicates that their main problem is product integration rather than conceptual absence. `workflow_runner.py`, the graph, and the RAG components already exist.

---

## 4.2 Source code is the source of truth

Never trust documentation blindly.

Before changing anything:

1. Inspect the relevant source code.
2. Understand the existing behavior.
3. Trace dependencies.
4. Confirm the expected inputs and outputs.
5. Then implement.

---

## 4.3 Do not create fake functionality

Never replace missing functionality with another mock simply to make the UI appear complete.

In particular:

* Do not fake CV predictions.
* Do not fake AI reports.
* Do not fake RAG results.
* Do not hardcode successful analysis states.

Development-only mocks may exist behind explicit test/development configuration, but production paths must execute real logic.

---

## 4.4 Every phase must leave the repository runnable

After each phase:

* backend must still start
* frontend must still build
* imports must remain valid
* migrations must be valid
* existing working functionality must not regress

---

## 4.5 Do not jump phases

An AI coding agent must NOT skip ahead.

Complete one phase.

Validate it.

Then proceed.

If a blocking dependency is discovered, stop that phase and fix the dependency before continuing.

---

# 5. IMPLEMENTATION STATUS MODEL

Track every major task using:

* `NOT_STARTED`
* `IN_PROGRESS`
* `BLOCKED`
* `COMPLETED`
* `VERIFIED`

Never mark a task `COMPLETED` merely because code was written.

It must also be tested.

---

# PHASE 0 — BASELINE AND SAFE TAKEOVER

## Objective

Establish a clean, reproducible baseline before modifying application behavior.

## Tasks

### 0.1 Inspect repository state

Inspect:

* Git status
* existing branches
* package managers
* Python environment
* Node environment
* Docker setup
* environment files
* migrations
* startup scripts

### 0.2 Document how the project currently runs

Confirm:

* backend startup command
* frontend startup command
* database startup
* Docker startup
* seed process
* test scripts

### 0.3 Establish a baseline

Run the existing application where possible.

Record:

* backend starts?
* frontend starts?
* database connects?
* login works?
* building CRUD works?
* inspection creation works?
* image upload works?
* analysis endpoint works?
* CLI LangGraph workflow works?

### 0.4 Create baseline notes

Do not modify architecture yet.

Document actual observed behavior.

## Exit Criteria

The project can be started and the current state is reproducible.

---

# PHASE 1 — UNDERSTAND AND LOCK THE DATA MODEL

## Objective

Ensure the database can represent the full target workflow.

The audit identified an important gap: the existing `Assessment` model contains risk/severity information but does not adequately persist the generated recommendation/report and RAG context.

## Tasks

Inspect all models before editing.

Determine the relationships between:

```text
User
 ↓
Building
 ↓
Floor
 ↓
Area
 ↓
StructuralElement
 ↓
Defect
 ↓
Inspection
 ↓
Image
 ↓
Observation
 ↓
Assessment
```

Then design the minimum schema needed to persist:

### Inspection

* inspection identity
* inspector
* location
* timestamps
* status

### Image

* storage key/path
* metadata
* upload state

### Observation

* image association
* detected defect
* manually entered observations

### Assessment

At minimum consider:

* defect type
* confidence
* severity
* risk score/category
* priority
* recommended action
* analysis status
* model metadata
* analysis timestamp

### AI Report

Determine whether the report belongs inside `Assessment` or deserves a dedicated entity.

Consider storing:

* report text / structured report
* executive summary
* recommendations
* citations/references
* generated timestamp
* model/version information
* workflow version

### Job / Analysis

Consider a separate analysis-job entity if asynchronous processing is introduced.

Potential state values:

```text
QUEUED
PROCESSING
COMPLETED
FAILED
CANCELLED
```

## Important

Do not automatically add fields merely because they sound useful.

Base the final schema on the actual graph state and the response structure produced by the current LangGraph implementation.

## Exit Criteria

The database can persist the complete output of a real analysis.

---

# PHASE 2 — REAL COMPUTER VISION INFERENCE

## Objective

Replace the hardcoded ML response with actual model inference.

The audit confirmed that `MLService` currently returns dummy output and does not load the existing `.keras` model.

## Tasks

Inspect:

```text
civilcortex_best.keras
ml_service.py
cv_pipeline
model-related configuration
test scripts
```

Determine:

* model architecture
* expected image size
* preprocessing
* classes
* output format
* confidence interpretation
* model framework/version compatibility

Do NOT guess these values.

Extract them from:

* existing inference code
* training metadata
* configuration
* model structure
* documentation
* test artifacts

## Implement

Create a reliable inference service.

Conceptually:

```text
Uploaded image
      ↓
Load/validate image
      ↓
Preprocess exactly as model expects
      ↓
Run Keras inference
      ↓
Interpret output
      ↓
Return normalized result
```

Example normalized internal result:

```json
{
  "defect_type": "...",
  "confidence": 0.0,
  "model_version": "..."
}
```

Do not hardcode the prediction.

## Validation

Test with:

* valid image
* invalid image
* unsupported file
* corrupted image
* very large image
* multiple supported image formats

## Exit Criteria

The API can perform real CV inference using the intended model.

---

# PHASE 3 — DEFINE THE AI CONTRACT

## Objective

Before wiring LangGraph into FastAPI, define a stable contract between:

```text
CV
↓
Assessment Logic
↓
LangGraph
↓
Report
```

This is one of the most important architectural steps.

Do not directly couple FastAPI routes to internal LangGraph node implementation.

Create a clear application-level analysis input.

Conceptually:

```text
AnalysisInput

inspection_id
image_id
building context
location context
structural element
defect observation
CV result
```

And an output:

```text
AnalysisResult

risk
severity
priority
planning information
RAG evidence
recommendation
executive report
metadata
```

The exact schema must be based on the existing graph state.

## Goal

The rest of the application should not need to know:

* how many LangGraph nodes exist
* how state is internally represented
* how ChromaDB is called
* how Gemini is called

It should consume a stable service interface.

---

# PHASE 4 — INTEGRATE LANGGRAPH INTO THE BACKEND

## Objective

Connect the existing LangGraph workflow to the actual backend.

The audit identified `workflow_runner.py` as orphaned from the REST application.

## Tasks

Inspect:

```text
backend/app/agents/graph.py
backend/app/services/workflow_runner.py
agent nodes
state definitions
test_graph.py
test_hallucination.py
```

Determine:

1. Graph input
2. Graph state
3. Graph output
4. Exceptions
5. External API calls
6. RAG dependencies
7. Execution duration
8. Required environment variables
9. Whether the graph is deterministic where intended

## Create an integration service

Conceptually:

```text
analysis_service.py
```

Responsibilities:

1. Validate analysis request.
2. Gather application data.
3. Invoke CV.
4. Construct graph input.
5. Run graph.
6. Validate graph output.
7. Persist results.
8. Return application-level result.

Do NOT put all of this into `inspections.py`.

Routes should remain thin.

---

# PHASE 5 — CONNECT RAG PROPERLY

## Objective

Make the RAG knowledge base part of the actual user-facing workflow.

The existing RAG engine uses ChromaDB and engineering knowledge files, but currently operates outside the web flow.

## Tasks

Verify:

* what documents are indexed
* embedding model
* chunking
* metadata
* retrieval top-k
* similarity threshold
* citation/reference format
* initialization process

Ensure the retrieved context corresponds to the actual defect.

The pipeline should approximately be:

```text
Defect Information
      ↓
Query construction
      ↓
ChromaDB retrieval
      ↓
Relevant standards/context
      ↓
Structured evidence
      ↓
LLM generation
```

The report must not pretend that a regulation was retrieved when retrieval actually failed.

## Failure handling

If no relevant knowledge is found:

* do not fabricate standards
* explicitly indicate insufficient evidence
* allow engineer review

---

# PHASE 6 — CONNECT GEMINI REPORT GENERATION

## Objective

Turn the graph output into a useful engineering decision-support report.

The current LangGraph architecture already includes a Gemini-based synthesis stage.

## Report structure

The final report should be structured rather than being an arbitrary block of text.

At minimum consider:

```text
Inspection Summary
Detected Defect
Confidence
Severity
Risk
Priority
Observed Evidence
Relevant Standards / References
Recommended Action
Required Resources
Recommended Follow-up
Limitations / Uncertainty
Engineer Review Status
```

The actual fields must align with the graph's existing capabilities and the product requirements.

## Important safety principle

The system is a decision-support tool.

It must NOT represent an AI-generated recommendation as a final engineering approval.

The UI and report should clearly distinguish:

```text
AI Recommendation
vs.
Engineer Decision
```

---

# PHASE 7 — INTRODUCE ASYNCHRONOUS ANALYSIS

## Objective

Prevent long-running AI analysis from blocking normal HTTP requests.

The audit estimates LangGraph execution at roughly 10–15+ seconds and identifies synchronous execution as a scalability/UX concern.

## First determine the smallest sufficient mechanism.

Evaluate:

### Option A

FastAPI BackgroundTasks

### Option B

Existing Redis infrastructure + task worker

### Option C

Celery / equivalent task queue

Do NOT automatically introduce Celery simply because it is listed in the original report.

Choose based on:

* expected workload
* reliability needs
* deployment architecture
* retry requirements
* current Docker infrastructure
* complexity

For a true production workload, a durable queue is preferable to a basic in-process background task.

## Recommended state flow

```text
POST /analysis
      ↓
Create job
      ↓
Return job ID
      ↓
Worker starts
      ↓
CV
      ↓
LangGraph
      ↓
RAG
      ↓
Gemini
      ↓
Persist result
      ↓
COMPLETED
```

Frontend:

```text
Create job
   ↓
Poll job status / receive events
   ↓
Show progress
   ↓
Display report
```

---

# PHASE 8 — COMPLETE THE API

## Objective

Create clean application-level APIs for the complete lifecycle.

The exact routes must follow the existing project conventions.

Potential resource model:

```text
POST   /inspections
POST   /inspections/{id}/images
POST   /inspections/{id}/analysis
GET    /analysis/{job_id}
GET    /inspections/{id}/assessment
GET    /inspections/{id}/report
PATCH  /assessments/{id}
```

Do not blindly create every route above.

First reconcile them with the existing API.

## API requirements

All analysis APIs should define:

* input validation
* authentication
* authorization
* success response
* validation errors
* processing state
* failure state
* not-found behavior

Use consistent response formats.

---

# PHASE 9 — FIX FILE STORAGE

## Objective

Replace fragile local file storage with the project's intended object storage architecture.

The audit notes that MinIO is provisioned in Docker but the current image service still stores files locally.

## Tasks

Determine whether MinIO is the right storage target for this project.

If yes:

```text
Frontend
 ↓
FastAPI
 ↓
Object storage
 ↓
Database stores object key
```

The database should generally store metadata/object identity rather than depending on arbitrary local filesystem paths.

## Requirements

Implement:

* unique object names
* content validation
* size limits
* safe extensions
* MIME validation
* controlled downloads
* cleanup strategy
* failure recovery

---

# PHASE 10 — FRONTEND: REBUILD THE REAL INSPECTION FLOW

## Objective

Make the React application reflect the actual product rather than merely CRUD.

The current `NewInspection` flow stops after mocked analysis and does not display an LLM report.

## Target flow

```text
Create Inspection
      ↓
Select structural location
      ↓
Upload image
      ↓
Preview image
      ↓
Start analysis
      ↓
Processing state
      ↓
CV result
      ↓
Engineering assessment
      ↓
Report
      ↓
Engineer review
```

## UI states

Explicitly support:

```text
IDLE
UPLOADING
QUEUED
ANALYZING
REPORT_GENERATING
COMPLETED
FAILED
```

Do not show fake "instant AI results."

---

# PHASE 11 — BUILD THE ENGINEER REPORT EXPERIENCE

## Objective

Create the missing UI that exposes the project's primary value.

Create a dedicated report/assessment screen.

It should display, as applicable:

### Inspection Context

* Building
* Floor
* Area
* Structural Element
* Inspector
* Date

### Visual Assessment

* Uploaded image
* Detected defect
* Confidence
* Evidence

### Risk Assessment

* Severity
* Risk
* Priority

### Standards Evidence

* Retrieved references
* Relevant excerpts or citations
* Source metadata where available

### Recommendation

* Recommended action
* Required resources
* Priority
* Follow-up

### AI Transparency

Display:

* generated by AI
* model information where appropriate
* limitations
* confidence/uncertainty
* timestamp

### Engineer Decision

Provide a human review mechanism such as:

```text
Approve
Reject
Request Reinspection
Add Comment
Override Recommendation
```

The exact workflow should be based on the intended roles and business requirements.

---

# PHASE 12 — IMPLEMENT RBAC

## Objective

Separate field inspection permissions from engineering review permissions.

The audit confirms that authentication exists but true Inspector vs Lead Engineer role separation does not.

## Define roles

At minimum evaluate:

```text
INSPECTOR
ENGINEER
ADMIN
```

Potential permissions:

### Inspector

* create inspections
* upload images
* add observations
* view own assigned work

### Engineer

* review assessments
* review reports
* approve/reject recommendations
* modify engineering decision

### Admin

* manage users
* manage buildings
* system configuration

Do not assume these exact permissions without checking the project's intended requirements.

## Enforcement

Authorization must exist on the backend.

Frontend route hiding alone is NOT security.

---

# PHASE 13 — SECURITY HARDENING

## Objective

Make the system safe enough for realistic usage.

The audit identifies issues including hardcoded secrets and file-validation weaknesses.

## Tasks

Review:

* secret management
* JWT configuration
* password hashing
* token expiry
* CORS
* authorization
* object access
* file uploads
* file type validation
* file size limits
* path handling
* API rate limiting
* error leakage
* AI output rendering
* dependency vulnerabilities

## LLM output

Never blindly trust generated Markdown/HTML.

Sanitize rendered content appropriately.

Do not allow AI output to become an arbitrary HTML/script execution vector.

---

# PHASE 14 — ERROR HANDLING AND OBSERVABILITY

## Objective

Make failures understandable.

Every major layer should produce meaningful errors.

Example:

```text
Image Upload Failed
CV Failed
RAG Retrieval Failed
LLM Failed
Database Save Failed
Analysis Job Failed
```

Avoid returning generic:

```text
500 Internal Server Error
```

without logging the actual cause internally.

## Add

* structured logging
* request IDs
* analysis/job IDs
* timestamps
* error categories
* safe frontend error messages

Do not expose secrets or stack traces to end users.

---

# PHASE 15 — TESTING FOUNDATION

## Objective

Replace the current manual-test-heavy approach with automated verification.

The audit confirms there is no meaningful pytest suite and no frontend test suite.

## Backend

Create tests for:

### Authentication

* login success
* invalid credentials
* token validation
* unauthorized access

### Hierarchy

* building creation
* ownership
* nested relationships

### Inspection

* creation
* image upload
* invalid image
* access restrictions

### AI

* CV inference contract
* workflow input/output
* RAG retrieval
* failure handling

### Analysis jobs

* queued
* processing
* completed
* failed

### Authorization

Test every protected role.

---

# PHASE 16 — FRONTEND TESTING

## Objective

Protect the most important user journeys.

Test:

```text
Login
→ Create inspection
→ Upload image
→ Start analysis
→ Observe processing
→ View completed report
→ Review assessment
```

Also test:

* API failure
* expired authentication
* unauthorized role
* failed AI analysis
* empty results

---

# PHASE 17 — END-TO-END VALIDATION

## Objective

Prove that the COMPLETE product works.

One golden-path test should execute:

```text
Login
↓
Create building hierarchy
↓
Create inspection
↓
Upload real image
↓
Trigger analysis
↓
Real CV inference
↓
LangGraph
↓
RAG retrieval
↓
Gemini
↓
Persist assessment
↓
Persist report
↓
Frontend displays report
↓
Engineer reviews result
```

This is the most important validation in the entire roadmap.

A project is NOT considered "AI integrated" until this path works.

---

# PHASE 18 — PERFORMANCE AND RELIABILITY

## Objective

Measure the actual system rather than guessing.

Measure:

* image upload duration
* CV inference time
* RAG retrieval time
* Gemini latency
* total analysis time
* API latency
* database latency
* queue time

Then identify bottlenecks.

Do not optimize prematurely.

---

# PHASE 19 — DATABASE AND SEARCH OPTIMIZATION

## Objective

Prepare the system for realistic data volumes.

Review:

* indexes
* foreign keys
* query patterns
* pagination
* search
* filtering
* historical reports

The original audit identified indexing as a future scalability requirement.

Add indexes based on actual query patterns rather than indexing every field.

---

# PHASE 20 — DEPLOYMENT HARDENING

## Objective

Move from development infrastructure toward deployment-ready infrastructure.

Review:

* Docker images
* production environment variables
* database configuration
* MinIO
* Redis/task worker
* frontend build
* reverse proxy
* HTTPS
* logging
* health checks
* startup ordering
* migrations

Ensure secrets are never committed.

---

# PHASE 21 — DOCUMENTATION

## Objective

Make the project maintainable after handover.

Create/update:

```text
README.md
ARCHITECTURE.md
API_DOCUMENTATION.md
DATABASE.md
AI_PIPELINE.md
DEPLOYMENT.md
DEVELOPMENT.md
TROUBLESHOOTING.md
```

Documentation must describe the ACTUAL implementation.

---

# 6. TARGET ARCHITECTURE AFTER IMPLEMENTATION

The expected logical architecture should resemble:

```text
Frontend
│
├── Authentication
├── Buildings
├── Inspections
├── Upload
├── Analysis Status
├── Assessment
└── Engineer Review
         │
         ▼
FastAPI
│
├── Auth
├── Buildings
├── Inspections
├── Images
├── Analysis
├── Assessments
└── Reports
         │
         ▼
Application Services
│
├── Auth Service
├── Inspection Service
├── Image Service
├── ML Service
├── Analysis Service
├── Report Service
└── Storage Service
         │
         ├───────────────┐
         ▼               ▼
      Database       Async Worker
                         │
                         ▼
                    LangGraph
                    │
                    ├── Risk logic
                    ├── Planning
                    ├── RAG
                    └── Gemini
```

The exact directory structure may differ as long as responsibilities remain cleanly separated.

---

# 7. IMPORTANT FILES TO PRESERVE / INSPECT

The existing analysis identifies these as especially important:

```text
backend/app/agents/graph.py
backend/app/agents/nodes/agent4_planning.py
backend/app/services/workflow_runner.py
backend/app/services/ml_service.py
backend/app/api/routes/inspections.py
backend/app/models/defect.py
frontend/src/pages/NewInspection.tsx
```

These represent the primary bridge between the current prototype and the target product.

Before modifying any one of them, inspect its callers and dependencies.

---

# 8. WHAT NOT TO DO

Do NOT:

### 8.1 Rewrite the whole backend

The current FastAPI architecture is already reasonably structured.

### 8.2 Rewrite the LangGraph pipeline immediately

First integrate and test it.

Only change nodes when an actual functional problem requires it.

### 8.3 Replace technology for fashion

Do not migrate frameworks, databases, frontend technologies, or AI frameworks unless there is a demonstrated technical reason.

### 8.4 Add unnecessary microservices

CivilCortex does not need ten services merely to look enterprise-grade.

Prefer a modular monolith with workers unless scale proves otherwise.

### 8.5 Add random AI agents

The project already contains a multi-agent architecture.

More agents do not automatically make the product better.

### 8.6 Optimize before measuring

First obtain real execution metrics.

### 8.7 Build cosmetic dashboard features before fixing the core journey

The primary value is:

```text
Image
→ Defect
→ Risk
→ Evidence
→ Recommendation
→ Engineer Review
```

That journey comes first.

---

# 9. DEFINITION OF MVP

CivilCortex should NOT be called an MVP until the following works:

## Authentication

* User can securely log in.
* Protected resources enforce authorization.

## Inspection

* User can create inspection.
* User can select structural location.
* User can upload an actual image.

## CV

* Actual `.keras` model performs inference.
* Result is persisted.

## AI Analysis

* LangGraph executes through the application.
* RAG retrieves engineering knowledge.
* Gemini generates the report.

## Persistence

* Analysis result is stored.
* Report is stored.
* Analysis status is stored.

## Frontend

* User can see analysis progress.
* User can see final assessment.
* User can read the generated report.

## Engineering Review

* Engineer can review AI output.
* Engineer can record a final decision.

## Reliability

* Failures are visible.
* Failed analyses can be retried safely.

---

# 10. DEFINITION OF PRODUCTION-READY

Production readiness requires more than the MVP.

The system should additionally have:

* secure secrets
* RBAC
* durable asynchronous processing
* proper storage
* automated tests
* monitoring
* logging
* health checks
* migration strategy
* input validation
* file security
* output sanitization
* error handling
* reproducible deployment
* model/version tracking
* rate limiting
* backup/recovery strategy
* performance validation

---

# 11. IMPLEMENTATION ORDER

The exact execution order is:

```text
PHASE 0
Baseline
   ↓
PHASE 1
Database / data model
   ↓
PHASE 2
Real CV inference
   ↓
PHASE 3
AI contract
   ↓
PHASE 4
LangGraph integration
   ↓
PHASE 5
RAG integration
   ↓
PHASE 6
Gemini report generation
   ↓
PHASE 7
Async processing
   ↓
PHASE 8
API completion
   ↓
PHASE 9
Object storage
   ↓
PHASE 10
Frontend analysis flow
   ↓
PHASE 11
Engineer report UI
   ↓
PHASE 12
RBAC
   ↓
PHASE 13
Security
   ↓
PHASE 14
Observability
   ↓
PHASE 15
Backend tests
   ↓
PHASE 16
Frontend tests
   ↓
PHASE 17
End-to-end validation
   ↓
PHASE 18
Performance
   ↓
PHASE 19
Database optimization
   ↓
PHASE 20
Deployment
   ↓
PHASE 21
Documentation
```

---

# 12. PHASE EXECUTION RULE FOR GEMINI / ANTIGRAVITY

When working on this repository, follow this exact process.

For every phase:

## Step 1 — Read

Read this `MASTER_IMPLEMENTATION_PLAN.md`.

Read the relevant sections of `PROJECT_ANALYSIS.md`.

Inspect the actual source code.

## Step 2 — Report

Before making significant modifications, state:

```text
Current Phase:
Objective:
Files inspected:
Current behavior:
Problem confirmed:
Planned changes:
Potential risks:
```

## Step 3 — Implement

Modify only files necessary for the current phase.

Do not perform unrelated refactoring.

## Step 4 — Validate

Run the relevant:

* backend tests
* frontend tests
* type checks
* build
* lint
* integration checks
* manual verification

## Step 5 — Update

Report:

```text
Phase:
Status:
Files changed:
Behavior changed:
Tests executed:
Tests passed:
Remaining issues:
```

## Step 6 — Stop

Do NOT silently continue into the next phase.

Wait until the current phase is verified before proceeding.

---

# 13. CHANGE MANAGEMENT RULES

For every significant code change:

Record:

```text
WHY
WHAT
WHERE
IMPACT
VALIDATION
```

Example:

```text
WHY:
The web application never invoked the LangGraph pipeline.

WHAT:
Added an analysis service that translates application data into graph input.

WHERE:
backend/app/services/analysis_service.py

IMPACT:
The API can now invoke the actual AI pipeline.

VALIDATION:
Integration test successfully completed.
```

---

# 14. AI SAFETY / ENGINEERING RESPONSIBILITY

CivilCortex operates in a domain where incorrect recommendations can have serious consequences.

Therefore the system must be presented as:

> **AI-assisted engineering decision support**

and not:

> **Autonomous engineering approval**

The application must maintain a clear human-review step.

AI-generated output should include sufficient traceability to explain:

* what was detected
* what evidence was used
* what standards/context were retrieved
* what recommendation was produced
* what uncertainty exists

The system must never fabricate regulatory evidence.

---

# 15. RECOMMENDED PRODUCT EVOLUTION

After the core MVP is stable, future development can explore:

## Advanced Vision

* crack segmentation
* crack width estimation
* crack length estimation
* severity classification
* multiple-defect detection
* image quality assessment

## Inspection Intelligence

* historical comparison
* deterioration tracking
* repeated inspection comparison
* location-based defect history

## Engineering Intelligence

* standard-aware recommendations
* evidence-linked reports
* configurable engineering rules
* engineer overrides
* audit trail

## Operational Intelligence

* maintenance prioritization
* inspection scheduling
* risk dashboards
* asset-level risk scoring
* maintenance history

## Advanced AI

Potential future capabilities:

* multimodal reasoning
* historical inspection retrieval
* report comparison
* anomaly detection
* predictive deterioration modeling

These are future capabilities.

They must NOT delay completion of the core MVP.

---

# 16. SUCCESS METRICS

The project should eventually measure:

### Technical

* CV inference latency
* analysis latency
* job success rate
* API error rate
* queue wait time
* database latency

### AI

* defect classification accuracy
* confidence calibration
* RAG retrieval relevance
* groundedness of generated reports
* unsupported recommendation rate

### Product

* time saved per inspection
* inspection-to-report time
* engineer review time
* percentage of reports requiring major correction
* user completion rate

The AI should be evaluated on usefulness and reliability, not merely whether Gemini produced text.

---

# 17. FINAL PRODUCT VISION

The final CivilCortex experience should feel like this:

```text
INSPECTOR

"Something looks wrong here."

        ↓

Upload evidence

        ↓

CIVILCORTEX

"We detected a probable crack."

        ↓

Analyze

        ↓

CIVILCORTEX

"Here is the estimated severity and risk."

        ↓

Retrieve relevant engineering standards

        ↓

CIVILCORTEX

"Here is the evidence and standards relevant
to this observation."

        ↓

Generate engineering decision-support report

        ↓

ENGINEER

"Review AI recommendation."

        ↓

Approve / Modify / Reject

        ↓

FINAL ENGINEERING DECISION
```

That is the product we are building toward.

---

# 18. FIRST IMPLEMENTATION PRIORITY

The first implementation objective is NOT the dashboard.

It is NOT a visual redesign.

It is NOT adding more agents.

It is:

```text
REAL IMAGE
   ↓
REAL CV
   ↓
REAL LANGGRAPH
   ↓
REAL RAG
   ↓
REAL GEMINI
   ↓
REAL DATABASE RECORD
   ↓
REAL REPORT IN UI
```

Until this works as one complete flow, CivilCortex has not achieved its core purpose.

---

# 19. FINAL INSTRUCTION TO AI CODING AGENTS

You are not being asked to blindly execute every recommendation in this document.

You must:

1. Inspect the current repository.
2. Verify assumptions.
3. Follow the phases in order.
4. Reuse existing good architecture.
5. Make the smallest justified change.
6. Test each phase.
7. Never fake missing functionality.
8. Never expose secrets.
9. Never skip validation.
10. Never silently jump to later phases.
11. Preserve backward compatibility where practical.
12. Keep documentation synchronized with implementation.

When uncertainty exists, prefer:

```text
INSPECT
→ VERIFY
→ DESIGN
→ IMPLEMENT
→ TEST
→ DOCUMENT
```

over:

```text
ASSUME
→ MODIFY
→ HOPE
```

---

# FINAL GOAL

Transform CivilCortex from:

> **A CRUD application with an isolated AI prototype**

into:

> **A coherent end-to-end structural inspection decision-support platform where real field evidence flows through computer vision, risk assessment, regulatory RAG, AI report generation, persistent storage, and human engineering review.**

The implementation is complete only when the complete golden path works end-to-end and is covered by automated verification.
