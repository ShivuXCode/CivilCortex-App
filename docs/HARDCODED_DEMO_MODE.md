# CivilCortex: Temporary Hardcoded Demo Mode (`1.jpg`, `7001-21.jpg`, `7001-115.jpg`, `7001-10.jpg`, `7001-1.jpg`, `7001-17.jpg`)

**Document ID:** `HARDCODED_DEMO_MODE`  
**Purpose:** Implementation of Filename-Triggered Hardcoded Demo Mode for Frontend Testing and Teaching Demonstrations  
**Trigger Filenames:** `1.jpg`, `7001-21.jpg`, `7001-115.jpg`, `7001-10.jpg`, `7001-1.jpg`, `7001-17.jpg` (and `.jpeg` equivalents)  
**Status:** **ACTIVE / VERIFIED**  

---

## 1. Purpose & Objectives

This demo mode provides a 100% deterministic, complete, and reproducible demonstration of the CivilCortex user interface, live telemetry metrics, regulatory compliance cards, and PDF report generation across a catalog of 6 real-world structural inspection scenarios.

When the user uploads any of the configured images, the system bypasses uncalibrated local ML models, Gemini LLM calls, and vector databases, instantly returning a verified structural triage inspection result matching the exact FHWA-aligned engineering specification.

---

## 2. Why Hardcoded Demo Mode Was Introduced

1. **Model Audit Findings:** The legacy `civilcortex_best.keras` model is a U-Net semantic segmentation network with uncalibrated thresholding rather than an image-level binary classifier.
2. **Reliable Presentation Experience:** Live demonstrations to teachers and stakeholders require instantaneous response times, zero risk of external API rate limits (Gemini 429 errors), and exact, consistent data across UI widgets.
3. **Preservation of Pipeline:** Rather than making breaking changes to the real ML pipeline or deleting existing LangGraph workflows, a clean router was added to isolate demo requests safely.

---

## 3. Exact Files Modified & Created

### Files Created:
* [`backend/demo/hardcoded_results.py`](file:///Users/vikram/Downloads/civilcortex/backend/demo/hardcoded_results.py): Contains the `HARDCODED_DEMO_RESULTS` dictionary and safe filename lookup helper `get_hardcoded_demo_result()`.
* [`backend/tests/test_hardcoded_demo.py`](file:///Users/vikram/Downloads/civilcortex/backend/tests/test_hardcoded_demo.py): Automated test suite validating `1.jpg`, `1.jpeg`, unknown images, and PDF exports.
* [`docs/HARDCODED_DEMO_MODE.md`](file:///Users/vikram/Downloads/civilcortex/docs/HARDCODED_DEMO_MODE.md): This technical documentation file.

### Files Modified:
* [`backend/api/routes.py`](file:///Users/vikram/Downloads/civilcortex/backend/api/routes.py): Added filename extraction and conditional dispatch to `get_hardcoded_demo_result()` in `POST /api/analyze-image`.
* [`backend/demo/__init__.py`](file:///Users/vikram/Downloads/civilcortex/backend/demo/__init__.py): Exported `HARDCODED_DEMO_RESULTS` and `get_hardcoded_demo_result`.
* [`backend/services/pdf_generator.py`](file:///Users/vikram/Downloads/civilcortex/backend/services/pdf_generator.py): Formatted PDF output to cleanly render the hardcoded telemetry, FHWA regulatory context, and action plan.

---

## 4. How `1.jpg` is Detected

Filename detection is handled safely without crashing on missing filenames, path separators, or casing:

```python
# backend/demo/hardcoded_results.py
def get_hardcoded_demo_result(filename: Optional[str]) -> Optional[Dict[str, Any]]:
    if not filename:
        return None
    # Strip any directory path components and convert to lowercase
    normalized_name = os.path.basename(filename).strip().lower()
    return HARDCODED_DEMO_RESULTS.get(normalized_name)
```

In `backend/api/routes.py`:
```python
if file:
    image_bytes = await file.read()
    mime_type = file.content_type or "image/jpeg"
    filename = getattr(file, "filename", "") or ""
    
    # 1. Check for Hardcoded Demo Result (e.g. 1.jpg / 1.jpeg)
    hardcoded_data = get_hardcoded_demo_result(filename)
    if hardcoded_data:
        result = dict(hardcoded_data)
        result["mode"] = "demo_hardcoded"
        result["filename"] = filename
        result["image_base64"] = f"data:{mime_type};base64," + base64.b64encode(image_bytes).decode("utf-8")
        ...
```

---

## 5. Exact Hardcoded Output for `1.jpg`

When `1.jpg` is processed, the backend returns the following exact structured response:

```json
{
  "crack_type": "Structural Crack",
  "severity": "high",
  "health_score": 0,
  "condition": "Critical",
  "risk_score": 85.0,
  "risk_level": "High",
  "priority": "Routine (Monitor)",
  "days": 30,
  "maintenance_action": "Based on FHWA_Bridge_Inspection, the standard requires: 4.2 STRUCTURAL CRACKING Structural cracks indicate potential load-bearing distress. Cracks wider than 0.05 inches (1.3 mm) in load-bearing substructures must be addressed via epoxy injection to restore structural integrity. If cracking is accompanied by active settlement, foundation underpinning is mandated.",
  "required_workers": 2,
  "required_materials": [
    "Polyurethane Sealant",
    "Wire Brushes",
    "Applicators"
  ],
  "estimated_cost": "$500 - $1,200",
  "rag_context": "Source: FHWA_Bridge_Inspection\nSection: 4.2 STRUCTURAL CRACKING\n\nStructural cracks indicate potential load-bearing distress. Cracks wider than 0.05 inches (1.3 mm) in load-bearing substructures must be addressed via epoxy injection to restore structural integrity. If cracking is accompanied by active settlement, foundation underpinning is mandated.\n\n4.3 NON-STRUCTURAL CRACKING (SHRINKAGE/TEMPERATURE)\nHairline cracks (< 0.01 inches) on bridge decks or retaining walls are typically non-structural. The standard maintenance action is surface sealing using polyurethane sealant to prevent water ingress and freeze-thaw damage.",
  "recommendation": "### Condition Summary\n- **Crack Type:** Structural Crack\n- **Health Score:** 0 / 100\n- **Overall Risk Level:** High\n- **Priority:** Routine (Monitor)\n\n---\n\n### Regulatory Compliance & Standards Justification\n**Source:** FHWA_Bridge_Inspection  \n**Section:** 4.2 STRUCTURAL CRACKING  \n\nStructural cracks indicate potential load-bearing distress. Cracks wider than 0.05 inches (1.3 mm) in load-bearing substructures must be addressed via epoxy injection to restore structural integrity. If cracking is accompanied by active settlement, foundation underpinning is mandated.\n\n**Section:** 4.3 NON-STRUCTURAL CRACKING (SHRINKAGE/TEMPERATURE)  \nHairline cracks (< 0.01 inches) on bridge decks or retaining walls are typically non-structural. The standard maintenance action is surface sealing using polyurethane sealant to prevent water ingress and freeze-thaw damage.\n\n---\n\n### Action Plan & Resource Requirements\n- **Proposed Action:** Based on FHWA_Bridge_Inspection, the standard requires: 4.2 STRUCTURAL CRACKING Structural cracks indicate potential load-bearing distress. Cracks wider than 0.05 inches (1.3 mm) in load-bearing substructures must be addressed via epoxy injection to restore structural integrity. If cracking is accompanied by active settlement, foundation underpinning is mandated.\n- **Estimated Cost:** $500 - $1,200\n- **Required Staffing:** 2 Workers\n- **Required Materials & Equipment:**\n  - Polyurethane Sealant\n  - Wire Brushes\n  - Applicators\n\n---\n\n### Next Steps & Recommendations\nPlease review the proposed action plan and dispatch the necessary engineering resources."
}
```

---

## 6. Architecture & Data Flow

```
                      USER (Browser)
                            │
                            ▼
                   Uploads "1.jpg"
                            │
                            ▼
                  POST /api/analyze-image
                            │
                            ▼
              ┌───────────────────────────┐
              │ get_hardcoded_demo_result │
              │   (Checks filename)       │
              └─────────────┬─────────────┘
                            │
                 MATCH: "1.jpg"
                            │
                            ▼
              ┌───────────────────────────┐
              │ HARDCODED_DEMO_RESULTS    │
              │ - Health Score: 0/100     │
              │ - Defect: Structural Crack│
              │ - Risk: High              │
              │ - Priority: Routine       │
              │ - Cost: $500 - $1,200     │
              │ - Crew: 2 Workers         │
              │ - RAG: FHWA Section 4.2   │
              └─────────────┬─────────────┘
                            │
                            ▼
              ┌───────────────────────────┐
              │ Persist Inspection to DB  │
              │ (Preserve image_base64)   │
              └─────────────┬─────────────┘
                            │
                            ▼
                 HTTP 200 JSON Response
                            │
                            ▼
              ┌───────────────────────────┐
              │ React Frontend            │
              │ - Telemetry Panel Cards   │
              │ - Chat Markdown Report    │
              │ - PDF Download Link       │
              └───────────────────────────┘
```

---

## 7. Unknown Images Behavior

If a file other than `1.jpg` (e.g. `bridge_sample.png`) is uploaded:
1. The system does **not** falsely assign the `1.jpg` structural crack result.
2. The system returns a polite, transparent notice:
   > **Demo Mode Notification**  
   > The uploaded image (`bridge_sample.png`) is not currently configured in the demonstration catalog.  
   > **Currently Available Demo Image:** `1.jpg` (or `1.jpeg`)  
   > Please upload **`1.jpg`** to preview the complete FHWA-compliant Structural Crack demonstration assessment.

---

## 8. Verification and Test Results

The test suite at `backend/tests/test_hardcoded_demo.py` executes 4 automated tests against the running FastAPI application:

```
--- Test 1: Uploading 1.jpg ---
Crack Type: Structural Crack
Health Score: 0
Risk Level: High
Priority: Routine (Monitor)
Estimated Cost: $500 - $1,200
Required Staffing: 2 workers
Required Materials: ['Polyurethane Sealant', 'Wire Brushes', 'Applicators']
RAG Context contains FHWA_Bridge_Inspection: True
Image base64 included: True
✓ Test 1: 1.jpg passed with 100% exact compliance!

--- Test 2: Uploading 1.jpeg ---
✓ Test 2: 1.jpeg alias passed!

--- Test 3: Uploading unknown image (e.g. random_bridge.png) ---
Unknown status: 200 (Mode: demo_notice)
✓ Test 3: Unknown image does not get 1.jpg result and returns clear demo notice!

--- Test 4: PDF Report Generation for 1.jpg inspection ---
✓ Test 4: PDF successfully generated for inspection #8 (3832 bytes)

ALL 4 HARDCODED DEMO MODE TESTS PASSED!
```

---

## 9. How to Add Additional Images (`2.jpg`, `3.jpg`, etc.)

To add new demonstration images in the future, simply add an entry to `HARDCODED_DEMO_RESULTS` in [`backend/demo/hardcoded_results.py`](file:///Users/vikram/Downloads/civilcortex/backend/demo/hardcoded_results.py):

```python
HARDCODED_DEMO_RESULTS["2.jpg"] = {
    "crack_type": "Hairline Crack",
    "severity": "low",
    "health_score": 88,
    "condition": "Fair",
    "risk_score": 32.0,
    "risk_level": "Medium",
    "priority": "Inspection / repair within 30 days",
    "days": 30,
    "maintenance_action": "Apply polyurethane surface sealant across hairline fissure.",
    "required_workers": 1,
    "required_materials": ["Polyurethane Sealant", "Wire Brush"],
    "estimated_cost": "$250 - $500",
    "rag_context": "Source: ACI 224.1R-07 Section 3.2...",
    "recommendation": "### Condition Summary\n- **Crack Type:** Hairline Crack..."
}
```

No API routes, schemas, or frontend changes are needed.

---

## 10. How to Remove Demo Mode Later

When real ML models are trained and ready for production:
1. In `backend/api/routes.py`, remove or bypass the `hardcoded_data = get_hardcoded_demo_result(filename)` check.
2. In `backend/core/config.py`, set `DEMO_MODE = False`.
3. The system will immediately route all uploads to `run_analysis(request)`.

---

## 11. Warning & Prototype Notice

> [!WARNING]
> **NOT REAL ML INFERENCE:** The output returned for `1.jpg` is a deterministic hardcoded demonstration payload designed for UI verification, classroom presentation, and stakeholder walkthroughs. It does not reflect genuine deep learning inference. Real ML model training code is isolated in `ml_pipeline/`.
