# CivilCortex: Demo Mode Implementation Report

**Document ID:** `DEMO_MODE_IMPLEMENTATION_REPORT`  
**Target System:** CivilCortex Multi-Agent Structural Health Assessment Platform  
**Implementation Scope:** Controlled, Fully Deterministic Demonstration Mode  
**Final Status:** **SUCCESS**  

---

## 1. Executive Summary

To enable a reliable, repeatable, and complete live demonstration of the CivilCortex structural triage workflow without dependency on uncalibrated ML weights or external cloud LLM APIs, a centralized **Controlled Demo Mode (`DEMO_MODE=true`)** was engineered.

### Key Highlights:
1. **Zero Destructive Changes:** All existing LangGraph nodes, database schemas, authentication systems, frontend layouts, PDF generators, and the `ml_pipeline/` files remain completely preserved.
2. **Deterministic Multi-Agent Pipeline:** When `DEMO_MODE=true` is set in `backend/core/config.py` (or `.env`), Agents 1 through 6 consume centralized scenario definitions without requiring an external Gemini API key, GPU, or internet connection.
3. **Real Image Upload Intact:** Users upload real inspection images; the image is received, validated, rendered on the frontend dashboard, saved to the database, and exported in the official PDF report.
4. **Interactive Scenario Selector:** Presenters can dynamically select between **4 Inspection Scenarios** directly from the UI or API:
   * **No Crack** (Clean Surface, Health: 100, Cost: ₹0)
   * **Hairline Crack** (Minor, Health: 88, Cost: ₹2,500 – ₹5,000) [Default]
   * **Moderate Crack** (Structural, Health: 68, Cost: ₹10,000 – ₹25,000)
   * **Severe Structural Crack** (Critical Emergency, Health: 35, Cost: ₹25,000 – ₹75,000)
5. **Empirical Verification:** 100% test pass rate across 7 unit and integration tests, including 20-run determinism verification and end-to-end PDF generation.

---

## 2. Architecture Comparison

### Existing Architecture vs. Demo Mode Architecture

```
                    IMAGE UPLOAD (Multipart Form)
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │ settings.DEMO_MODE?   │
                     └───────────┬───────────┘
                                 │
                   YES           │           NO
                    │            │            │
                    ▼            │            ▼
        ┌──────────────────────┐ │ ┌──────────────────────┐
        │  DEMO SCENARIO ENGINE│ │ │ Legacy Keras/Gemini  │
        │  (backend/demo/)     │ │ │ Vision Pipeline      │
        └───────────┬──────────┘ │ └──────────┬───────────┘
                    │            │            │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   AGENT 1: CONDITION   │
                    │   (Health, Defect,     │
                    │    Crack Probability)  │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │    AGENT 2: RISK       │
                    │   (Risk Score & Level) │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   AGENT 3: PRIORITY    │
                    │ (Turnaround Days: 1/7/30)
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   AGENT 4: PLANNING    │
                    │  (Standard Reference)  │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   AGENT 5: RESOURCES   │
                    │ (Workforce & INR Cost) │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   AGENT 6: REPORT      │
                    │ (Deterministic Markdown│
                    │  Executive Synthesis)  │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  PERSISTENCE & OUTPUT  │
                    │ - SQLite Database      │
                    │ - Live Telemetry UI    │
                    │ - Official PDF Report  │
                    └────────────────────────┘
```

---

## 3. Demo Scenarios Specification

All scenarios are centralized in `backend/demo/scenarios.py` and referenced across all agent nodes:

| Parameter | Scenario 1: No Crack | Scenario 2: Hairline Crack (Default) | Scenario 3: Moderate Crack | Scenario 4: Severe Structural Crack |
|---|---|---|---|---|
| **Scenario ID** | `no_crack` | `hairline_crack` | `moderate_crack` | `severe_crack` |
| **Crack Detected** | `False` | `True` | `True` | `True` |
| **Crack Probability** | `0.03` (3.0%) | `0.87` (87.0%) | `0.94` (94.0%) | `0.98` (98.0%) |
| **Defect Classification** | `None` | `Hairline Crack` | `Structural Crack` | `Severe Structural Crack` |
| **Visual Severity** | `low` | `low` | `medium` | `high` |
| **Health Score** | `100 / 100` | `88 / 100` | `68 / 100` | `35 / 100` |
| **Condition Category** | `Excellent` | `Fair` | `Poor` | `Critical` |
| **Risk Score** | `5.0 / 100` | `32.0 / 100` | `68.0 / 100` | `92.0 / 100` |
| **Risk Level** | `Low` | `Medium` | `High` | `Critical` |
| **Intervention Priority** | `Routine` | `Inspection / repair within 30 days` | `Repair within 7 days` | `Immediate inspection` |
| **Max Turnaround** | `30 Days` | `30 Days` | `7 Days` | `1 Day` (24 Hours) |
| **Recommended Action** | No immediate repair required. Continue periodic inspection. | Seal the crack and monitor for propagation. | Conduct detailed structural inspection and repair the affected region. | Restrict access if necessary and conduct immediate structural assessment. |
| **Repair Method** | Surface Cleaning & Periodic Monitoring | Low-Pressure Polyurethane Surface Sealing | Pressure Epoxy Injection & Mortar Patching | Section Shoring, Epoxy Grouting & CFRP Wrapping |
| **Workforce** | `0` workers | `1` technician | `3` technicians / inspectors | `5` engineers / repair crew |
| **Estimated Cost** | `₹0` | `₹2,500 – ₹5,000` | `₹10,000 – ₹25,000` | `₹25,000 – ₹75,000` |
| **Applicable Standards** | IS 456:2000 Section 35.3.2 | ACI 224.1R-07 Section 3.2 | ACI 546R-14 & IRC:SP:40 Clause 4.3 | FHWA-HRT-14-041 & IS 13920:2016 |

---

## 4. Component-by-Component Implementation Details

### A. Configuration (`backend/core/config.py`)
* Added `DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")`
* Added `DEFAULT_DEMO_SCENARIO: str = "hairline_crack"`
* Single source of truth across the entire backend.

### B. Demo Engine (`backend/demo/`)
* **`backend/demo/scenarios.py`:** Holds the complete dictionary of inspection scenarios and regulatory citations.
* **`backend/demo/demo_engine.py`:** Exposes helper functions `get_demo_scenario()`, `list_demo_scenarios()`, `get_demo_condition_state()`, and `get_demo_report_text()`.

### C. Agent 1: Condition Assessment (`backend/agents/nodes/agent1_condition.py`)
* If `settings.DEMO_MODE` is enabled:
  * Reads scenario from graph state (defaults to `hairline_crack`).
  * Yields deterministic detection, crack probability, defect subtype, severity, and health score.
* If `settings.DEMO_MODE` is disabled:
  * Executes the legacy ML model and Gemini Vision pipeline.

### D. Agent 2: Risk Assessment (`backend/agents/nodes/agent2_risk.py`)
* When in Demo Mode, pulls exact deterministic risk score and risk level mapped to the scenario.

### E. Agent 3: Priority Assessment (`backend/agents/nodes/agent3_priority.py`)
* When in Demo Mode, maps priority turnaround timeframes (30 Days, 7 Days, 1 Day).

### F. Agent 4: Maintenance Planning & Standards (`backend/agents/nodes/agent4_planning.py`)
* When in Demo Mode, injects verified regulatory standard citations (ACI, IS, FHWA) without requiring ChromaDB initialization.

### G. Agent 5: Resource Optimization (`backend/agents/nodes/agent5_resources.py`)
* When in Demo Mode, assigns exact material bill, workforce headcount, and INR cost estimates.

### H. Agent 6: Executive Synthesis (`backend/agents/nodes/agent6_llm.py`)
* When in Demo Mode, synthesizes an executive Markdown report containing Condition Summary, Risk & Priority, Recommended Strategy, Workforce/Material Allocations, Cost in INR, Standards Citations, and a clear Prototype Demo notice.

### I. API Layer (`backend/api/routes.py`)
* Added `GET /api/demo/status`: Returns current demo mode configuration and list of scenarios.
* Updated `POST /api/analyze-image`: Accepts optional `scenario: str = Form("hairline_crack")`, processes real uploaded images, runs the LangGraph graph, persists the inspection record with `mode: "demo"`, and returns the full telemetry payload.

### J. PDF Generator (`backend/services/pdf_generator.py`)
* Cleaned formatting to support INR currency strings (`INR 2,500 - 5,000`).
* Added automatic banner: `PROTOTYPE / DEMO MODE: Evaluated under controlled demonstration parameters.`
* Generates downloadable PDF reports directly from the inspection ID.

### K. Frontend Interface (`frontend/src/`)
* **`ChatBox.jsx`:** Added a clean, compact Demo Scenario dropdown selector (`No Crack`, `Hairline Crack`, `Moderate Crack`, `Severe Structural Crack`) above the input bar and passes `scenario` in the multipart form payload.
* **`TelemetryPanel.jsx`:** Added live Crack Probability indicator and colored status badges.
* **`App.jsx`:** Added a subtle `[DEMO]` indicator next to the CivilCortex brand header.

---

## 5. Files Modified and Created

### Files Created:
| File | Description |
|---|---|
| [`backend/demo/scenarios.py`](file:///Users/vikram/Downloads/civilcortex/backend/demo/scenarios.py) | Centralized demo scenario data and standards references |
| [`backend/demo/demo_engine.py`](file:///Users/vikram/Downloads/civilcortex/backend/demo/demo_engine.py) | Deterministic evaluation engine & report formatter |
| [`backend/demo/__init__.py`](file:///Users/vikram/Downloads/civilcortex/backend/demo/__init__.py) | Demo package initialization |
| [`backend/tests/test_demo_mode.py`](file:///Users/vikram/Downloads/civilcortex/backend/tests/test_demo_mode.py) | Automated test suite verifying scenarios, determinism, and PDF export |
| [`docs/DEMO_MODE_IMPLEMENTATION_REPORT.md`](file:///Users/vikram/Downloads/civilcortex/docs/DEMO_MODE_IMPLEMENTATION_REPORT.md) | This implementation document |

### Files Modified:
| File | Changes Made |
|---|---|
| [`backend/core/config.py`](file:///Users/vikram/Downloads/civilcortex/backend/core/config.py) | Added `DEMO_MODE` and `DEFAULT_DEMO_SCENARIO` configuration settings |
| [`backend/schemas/request_models.py`](file:///Users/vikram/Downloads/civilcortex/backend/schemas/request_models.py) | Added `scenario` field to `MaintenanceRequest` |
| [`backend/services/workflow_runner.py`](file:///Users/vikram/Downloads/civilcortex/backend/services/workflow_runner.py) | Passed `scenario`, `is_load_bearing`, and `structure_type` to graph initial state |
| [`backend/agents/state.py`](file:///Users/vikram/Downloads/civilcortex/backend/agents/state.py) | Added `scenario`, `crack_detected`, `crack_probability`, and `mode` to `AgentState` |
| [`backend/agents/nodes/agent1_condition.py`](file:///Users/vikram/Downloads/civilcortex/backend/agents/nodes/agent1_condition.py) | Added `settings.DEMO_MODE` conditional branch |
| [`backend/agents/nodes/agent2_risk.py`](file:///Users/vikram/Downloads/civilcortex/backend/agents/nodes/agent2_risk.py) | Added Demo Mode deterministic risk mapping |
| [`backend/agents/nodes/agent3_priority.py`](file:///Users/vikram/Downloads/civilcortex/backend/agents/nodes/agent3_priority.py) | Added Demo Mode priority & turnaround mapping |
| [`backend/agents/nodes/agent4_planning.py`](file:///Users/vikram/Downloads/civilcortex/backend/agents/nodes/agent4_planning.py) | Added Demo Mode regulatory citations fallback |
| [`backend/agents/nodes/agent5_resources.py`](file:///Users/vikram/Downloads/civilcortex/backend/agents/nodes/agent5_resources.py) | Added Demo Mode workforce and INR cost lookup |
| [`backend/agents/nodes/agent6_llm.py`](file:///Users/vikram/Downloads/civilcortex/backend/agents/nodes/agent6_llm.py) | Added Demo Mode deterministic report generator |
| [`backend/api/routes.py`](file:///Users/vikram/Downloads/civilcortex/backend/api/routes.py) | Added `GET /api/demo/status` and `scenario` parameter to `POST /api/analyze-image` |
| [`backend/services/pdf_generator.py`](file:///Users/vikram/Downloads/civilcortex/backend/services/pdf_generator.py) | Enhanced PDF generator for INR currency, demo banner, and clean markdown |
| [`frontend/src/components/ChatBox.jsx`](file:///Users/vikram/Downloads/civilcortex/frontend/src/components/ChatBox.jsx) | Added Demo Scenario dropdown and passed `scenario` in upload payload |
| [`frontend/src/components/TelemetryPanel.jsx`](file:///Users/vikram/Downloads/civilcortex/frontend/src/components/TelemetryPanel.jsx) | Added Crack Probability and condition telemetry |
| [`frontend/src/App.jsx`](file:///Users/vikram/Downloads/civilcortex/frontend/src/App.jsx) | Added Demo Mode badge in sidebar |

---

## 6. Verification and Test Results

### Automated Unit & Integration Tests (`backend/tests/test_demo_mode.py`):
```
Running Demo Mode Tests...
✓ test_list_demo_scenarios passed (4 scenarios verified)
✓ test_scenario_1_no_crack passed (Health: 100, Detected: False, Cost: ₹0)
✓ test_scenario_2_hairline_crack passed (Health: 88, Severity: low, Cost: ₹2.5k-5k)
✓ test_scenario_3_moderate_crack passed (Health: 68, Severity: medium, Cost: ₹10k-25k)
✓ test_scenario_4_severe_crack passed (Health: 35, Severity: high, Cost: ₹25k-75k)
✓ test_determinism_20_iterations passed (20 sequential runs: 100% identical outputs)
✓ test_pdf_generation_demo passed (Generated 3.6 KB valid PDF)

ALL 7 DEMO MODE UNIT TESTS PASSED!
```

### End-to-End API and PDF Validation:
* **Endpoint:** `POST /api/analyze-image` (with sample image and `scenario="moderate_crack"`):
  * **HTTP Status:** `200 OK`
  * **Inspection ID:** Generated `#3`
  * **Saved Record:** Stored in SQLite database
  * **Image Preview:** Preserved base64 data
* **PDF Endpoint:** `GET /api/inspections/3/pdf`:
  * **HTTP Status:** `200 OK`
  * **Content Type:** `application/pdf`
  * **Payload Size:** `3,699 bytes`

---

## 7. How to Run the Presentation Demo

### Step 1: Start Backend API Server
```bash
cd backend
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```
Backend API will be running at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Step 2: Start Frontend Application
```bash
cd frontend
npm run dev
```
Frontend Web UI will be running at [http://localhost:5173](http://localhost:5173).

### Step 3: Presenting the Demonstration Flow
1. Open [http://localhost:5173](http://localhost:5173) in your browser.
2. Sign in or register with any test credentials.
3. In the chat interface, notice the **`PROTOTYPE DEMO MODE`** indicator and the **`Inspection Scenario`** dropdown above the input bar.
4. Click the `+` button and upload any structural/concrete image.
5. Select a scenario (e.g. **Hairline Crack**).
6. Press Submit:
   * View live AI agent telemetry updating in the right panel:
     * **Health Score:** `88/100 (Fair)`
     * **Crack Probability:** `87.0% (Crack)`
     * **Risk Level:** `Medium (32/100)`
     * **Priority:** `Inspection / repair within 30 days`
     * **Estimated Cost:** `₹2,500 – ₹5,000`
     * **Required Workforce:** `1 technician`
   * Read the official Markdown engineering report with regulatory standard citations.
7. Click **"Download Official Report (PDF)"** in the right panel to download the generated PDF.
8. Switch scenario to **"Severe Structural Crack (Critical)"** and submit another image to demonstrate how the risk rises to `92/100`, turnaround shifts to `Immediate (24 hours)`, cost adjusts to `₹25,000 - ₹75,000`, and shoring/CFRP actions are prescribed.

---

## 8. How to Switch Back to Real ML

To disable Demo Mode and revert to the real ML inference pipeline:

1. In `backend/.env` (or environment variables), set:
   ```bash
   DEMO_MODE=false
   ```
2. Restart the backend server:
   ```bash
   cd backend
   .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
   ```
3. Agent 1 will automatically switch to evaluating via the Keras model (`civilcortex_best.keras` or `crack_binary_classifier.keras`) and Gemini Vision.

---

## 9. Known Limitations & Prototype Disclaimer

* **Prototype Simulation:** Demo Mode outputs are predetermined engineering scenarios designed for system architecture demonstration. They do not constitute on-site physical engineering assessments.
* **Currency Formatting:** Costs are estimated in Indian Rupees (INR `₹`), structured as ballpark civil maintenance estimates.
* **Real ML Pipeline Status:** The genuine transfer-learning binary classification pipeline (`ml_pipeline/train_binary.py`) remains ready in `ml_pipeline/` for full training once a labelled dataset is provided.

---

## 10. Final Status

```
CivilCortex Demo Mode implementation completed.
Status: SUCCESS
```
