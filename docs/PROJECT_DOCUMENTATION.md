# CivilCortex: Project Documentation & Architecture Guide

## 1. Abstract & System Purpose
**CivilCortex** is an AI-driven, multi-agent infrastructure designed for automated defect detection, risk assessment, and maintenance recommendation in civil structures (e.g., tunnels, bridges, foundations).

The core objective is streamlining structural engineering triage by combining:
1. **Deterministic physical/structural rule engines** for condition scoring and risk assessment.
2. **LangGraph agent orchestration** with shared graph state across 6 specialized nodes.
3. **Retrieval-Augmented Generation (RAG)** via **ChromaDB** and **Gemini Embeddings** to ground recommendations in real-world regulatory standards.
4. **Computer Vision & Multimodal Inspection** (CNN/U-Net + Gemini Vision) for defect identification.

---

## 2. System Architecture

```
[Inspector Upload: Defect Image & Metadata]
                       │
                       ▼
            ┌─────────────────────┐
            │   Agent 1: Condition │ ──► (Local Vision / Segmentation & Severity)
            └──────────┬──────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
┌──────────────────┐       ┌──────────────────┐
│   Agent 2: Risk   │       │ Agent 3: Priority│
└────────┬─────────┘       └────────┬─────────┘
         │                          │
         ▼                          ▼
┌──────────────────┐       ┌──────────────────┐
│ Agent 4: Planning│       │Agent 5: Resources│
│  (RAG Retrieval) │       │ (Cost & Material)│
└────────┬─────────┘       └────────┬─────────┘
         │                          │
         └─────────────┬────────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │   Agent 6: LLM      │ ──► (Executive Synthesis grounded in RAG)
            └──────────┬──────────┘
                       │
                       ▼
          [Final Engineering Report]
```

### LangGraph 6-Agent Pipeline:
* **Node 1: Condition Assessment (`Agent1_Condition`)**: Evaluates raw physical parameters and image defects, computing `health_score` (0-100) and `condition` (Critical, Fair, Excellent).
* **Node 2: Risk Assessment (`Agent2_Risk`)**: Computes `risk_score` and `risk_level` (Low, Medium, High) considering delay risk and site compliance.
* **Node 3: Priority Assessment (`Agent3_Priority`)**: Maps risk and condition into actionable turnaround timeframes (Routine, Urgent, Immediate) with maximum response days.
* **Node 4: Maintenance Planning & RAG (`Agent4_Planning`)**: Queries ChromaDB vector store with regulatory engineering standards for the specific defect category.
* **Node 5: Resource Optimization (`Agent5_Resources`)**: Computes required workforce, material allocations, and estimated remediation budget.
* **Node 6: Executive Synthesis (`Agent6_LLM`)**: Produces a formal, compliant engineering recommendation citing the retrieved regulatory standards.

---

## 3. Technology Stack

* **Backend**: FastAPI, Uvicorn, SQLAlchemy, Pydantic, FPDF2, Python-dotenv
* **Orchestration & AI**: LangGraph, LangChain, Google Generative AI (Gemini 3.6 Flash / Gemini Embeddings), ChromaDB
* **Machine Learning & Vision**: TensorFlow / Keras, OpenCV, Scikit-image, PIL
* **Frontend**: React 19, Vite, Lucide React, Axios, React Router, React Markdown
* **Database**: SQLite (local development) / PostgreSQL (production)
