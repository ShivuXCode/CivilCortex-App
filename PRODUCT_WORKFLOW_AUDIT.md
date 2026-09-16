# CivilCortex Product & Workflow Audit

## Executive Summary
This audit evaluates the CivilCortex application from a domain and product design perspective, focusing on civil engineering workflows, data models, and the boundary between AI automation and human judgment. The core pipeline (Image -> CV -> LangGraph -> LLM Report -> Engineer Review) is functionally present. However, the system currently suffers from semantic ambiguities regarding how AI predictions are mapped to physical structural elements, and a rigid data lifecycle that does not adequately preserve audit trails when humans override AI decisions.

## Intended Product
CivilCortex is intended to be an AI-assisted structural inspection platform where field inspectors capture images of concrete defects, an AI pipeline analyzes the defects against regulatory standards (RAG) to generate a preliminary engineering report, and a qualified civil engineer reviews, overrides, and approves the final assessment for maintenance planning.

## Current Product
The current implementation successfully executes the intended technical pipeline. However, from a product perspective, it treats AI outputs as mutable database fields rather than immutable evidence, heavily conflates "Candidate Defects" with confirmed physical defects, and assumes a simplistic lifecycle that lacks true auditability.

## Domain Entity Analysis

- **User:** Represents all humans (Inspectors and Engineers) in the system. The model currently lacks roles, treating all users identically.
- **Building / Floor / Area:** The hierarchical spatial context. Ownership is rigidly assigned to a single User via `Building.owner_id`.
- **StructuralElement:** The physical concrete entity (e.g., Column 3A). Currently optional on Defects.
- **Inspection:** A time-bound field event performed by a User.
- **InspectionImage:** The visual evidence uploaded during an Inspection.
- **Defect:** A physical anomaly on a structural element. Currently, the system uses this to represent both *potential* defects identified by AI and *confirmed* defects.
- **CrackObservation:** The junction between an Inspection, Image, and Defect.
- **Assessment:** The risk and severity evaluation of an observation, holding both AI predictions and Human overrides.
- **AnalysisJob:** The background worker tracking task for CV/LLM execution.

## End-to-End Workflow
Status: CONFIRMED
1. User creates Inspection.
2. User uploads Image (`InspectionImage`).
3. User creates/triggers AnalysisJob.
4. CV Model segments the image and naive `np.max` determines defect presence.
5. If positive, a `Defect` and `CrackObservation` are generated.
6. RAG retrieves standards from ChromaDB.
7. LangGraph Agent orchestrates Gemini LLM to generate an `Assessment`.
8. Engineer reviews and overrides the `Assessment` properties via the Frontend UI.

## Inspection Lifecycle
Status: INFERRED
Inspections are open-ended collections of images. There is no concept of "closing" or "completing" an Inspection in the current data model.

## Defect Lifecycle
Status: CONFIRMED
Defects transition through states: `CANDIDATE` -> `MONITORED` / `DISMISSED` -> `REPAIRED`. The AI creates a `CANDIDATE` defect automatically upon CV confidence > 0.5.

## Assessment Lifecycle
Status: CONFIRMED
The Assessment is created entirely by the LangGraph AI pipeline. Once generated, an Engineer can use a `PATCH` endpoint to directly overwrite the `severity`, `risk`, and `repair_recommendation`. 

## Analysis Job Lifecycle
Status: CONFIRMED
Managed via Redis queue: `QUEUED` -> `PROCESSING` -> `COMPLETED` / `FAILED`. Idempotency is supported (failed jobs can be re-queued).

## Structural Element Association
The project previously made `structural_element_id` nullable on `Defect`.
1. **Is this a domain problem?** Yes. An image contains a crack, but an AI does not know *what* the crack is on unless told.
2. **Is nullable correct?** Making it nullable allows the AI to log "I saw a crack" without tying it to a known column. However, it breaks the core engineering requirement: a crack's severity depends entirely on the element it affects (a crack on a load-bearing column is critical; on a floor slab, it might be minor).
3. **Should AI create candidate defects?** Yes, to flag issues, but they shouldn't pollute the Structural Element's history until confirmed.
4. **Should StructuralElement be mandatory?** Field inspectors should be required to tag the element at the time of image capture. If unknown, they should tag a generic "Unknown Area" rather than breaking the relational model.

## AI vs Engineer Responsibility
Status: INFERRED
Currently, the AI determines the initial severity, risk, and recommendation. Engineers review and modify this. 
**Flaw:** The Engineer `PATCH` overwrites the AI's values directly in the `Assessment` table. The system loses the original AI prediction. There is no audit trail proving what the AI initially recommended versus what the Engineer changed it to, which is a massive liability risk in structural engineering.

## User Roles
Status: CONFIRMED
The system does not currently distinguish between Inspector and Engineer. Anyone who owns the Building can capture images and overwrite engineering assessments.

## Report Workflow
Status: CONFIRMED
If Gemini fails (e.g., rate limit or missing credentials), the LangGraph node falls back to a standardized JSON/Markdown string indicating manual review is required. This correctly prevents system crashes, but relies heavily on the Engineer reading the fallback text rather than triggering a distinct UI error state.

## Data Traceability
Status: INFERRED
Traceability is broken.
"Why did the system make this recommendation?"
- Image -> CV mask (Mask is discarded, untraceable).
- CV mask -> Defect (Traceable via `CrackObservation`).
- RAG Evidence -> LLM Output (RAG context is saved to the DB, traceable).
- LLM Output -> Final Report (Overwritten by Engineer, untraceable).

## Current Workflow Gaps
1. **No Assessment Audit Trail:** Engineer edits destroy the original AI assessment.
2. **Disconnected Defects:** Nullable `structural_element_id` causes authorization fallback complexities and removes engineering context.
3. **No Inspection Sign-off:** No mechanism to lock an inspection from further uploads.

## Product Ambiguities
- **Does a Defect belong to an Element or an Image?** Currently, it's mapped 1-to-1 with a CrackObservation, which maps to an Image. A single physical Defect photographed twice will currently generate two distinct Defect records. 

## Recommended Product Decisions

### Structural Element Tagging
**Option A: Mandatory Element Tagging at Capture**
- *Behavior:* Inspector must select a Structural Element before taking a photo.
- *Advantages:* Enforces strict data hygiene; AI knows the load-bearing context.
- *Disadvantages:* Slows down field work if elements are missing from the DB.

**Option B: Optional Tagging, Required for Final Assessment** (Current path)
- *Behavior:* AI creates a floating defect; Engineer must link it later.
- *Advantages:* Fast field capture.
- *Disadvantages:* Complicates authorization; AI generates reports without load-bearing context, leading to inaccurate risk scores.

### Auditability of AI Assessments
**Option A: Separate AI vs Human Fields**
- *Behavior:* `Assessment` has `ai_risk` and `engineer_risk`.
- *Advantages:* Perfect traceability; easy schema change.
- *Disadvantages:* Clutters the data model.

**Option B: Immutable Assessments with Versions**
- *Behavior:* Engineer overrides create a new `AssessmentReview` record that supersedes the AI `Assessment`.
- *Advantages:* Enterprise-grade auditability; standard for civil engineering software.
- *Disadvantages:* Requires schema changes and UI updates.

## Critical Domain Decisions Before Production
1. Determine how to deduplicate physical defects (multiple images of the same crack).
2. Implement an immutable audit log for AI vs. Human decisions.

## Cross-Audit Dependencies
- **Security vs Workflow:** The decision to make `Defect.structural_element_id` nullable (Product Workflow) directly caused the complex, risky authorization fallback logic in `defects.py` (Security). 
- **ML vs Workflow:** The naive ML `np.max` confidence calculation (ML Audit) generates high false-positive Candidate Defects, which pollutes the product database with junk data (Workflow), eroding Engineer trust.
- **Security vs ML/RAG:** The AI agent securely falls back gracefully if Gemini errors (Security), but blindly accepts RAG documents into its prompt, tying product reliability entirely to the security/validity of the ChromaDB ingestion process.
