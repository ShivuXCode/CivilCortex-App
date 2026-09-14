# CivilCortex: Multi-Agent Structural Health Assessment & Maintenance System

## 1. Abstract & Project Purpose
CivilCortex is an advanced, AI-driven backend infrastructure designed for automated defect detection, risk assessment, and maintenance recommendation in civil structures (such as tunnels and foundations). 

The primary purpose of this project is to eliminate the manual bottleneck in structural engineering triage. By leveraging an Agentic Workflow (LangGraph) and Retrieval-Augmented Generation (RAG), the system processes structural anomalies (e.g., Deep Foundation Settlement, Spalling) and outputs an immediate, standards-compliant executive maintenance plan.

Unlike traditional single-prompt LLMs that are prone to hallucination, CivilCortex utilizes a sequential multi-agent pipeline where each "agent" serves a highly specific, deterministic engineering function before culminating in a final LLM-generated report grounded in real-world regulatory standards.

---

## 2. Technology Stack & Justification

*   **FastAPI & Uvicorn**: Chosen for the API layer due to its high performance, automatic OpenAPI documentation, and asynchronous capabilities. It acts as the bridge receiving defect reports from field inspectors/sensors.
*   **LangGraph**: The core orchestration engine. Instead of a monolithic script, LangGraph allows us to define the process as a directed graph where data passes through distinct "Nodes" (Agents). This makes the system modular, debuggable, and scalable.
*   **ChromaDB**: An open-source vector database used locally to store and query our engineering knowledge base. It provides fast similarity search for RAG.
*   **Google Generative AI (Gemini)**: 
    *   *gemini-embedding-2*: Used to convert text from the knowledge base into mathematical vectors for storage and retrieval.
    *   *gemini-1.5-flash-latest*: The reasoning engine used by the final agent to synthesize raw data and RAG context into a human-readable executive summary.
*   **Langchain**: Used as the integration layer to bridge ChromaDB, the embedding models, and the text splitters.

---

## 3. System Architecture: The 6-Agent LangGraph Workflow

The heart of CivilCortex is the `StateGraph` which manages an `AgentState`. The state acts as the shared memory that gets updated as it passes through 6 specialized nodes.

### Node 1: Condition Assessment (`Agent1_Condition`)
*   **Purpose**: Analyzes the raw physical parameters (e.g., crack type, length) and determines the immediate physical degradation.
*   **Mechanism**: Uses hardcoded, deterministic logic to assign a `health_score` (0-100) and a categorical `condition` (e.g., "Critical", "Fair"). 
*   **Why**: AI shouldn't guess basic physical degradation; deterministic logic ensures absolute reliability for baseline metrics.

### Node 2: Risk Assessment (`Agent2_Risk`)
*   **Purpose**: Evaluates the broader hazard posed by the defect.
*   **Mechanism**: Combines the initial severity with external factors (e.g., `helmet_compliance`, `delay_risk`) to calculate a mathematical `risk_score` and a `risk_level` (Low/Medium/High).

### Node 3: Priority Assessment (`Agent3_Priority`)
*   **Purpose**: Determines the urgency of the response.
*   **Mechanism**: Maps the Risk Level and Condition to an actionable `priority` (Routine/Urgent/Immediate) and specifies the maximum `days` allowed before remediation must begin.

### Node 4: Maintenance Planning & RAG Retrieval (`Agent4_Planning`)
*   **Purpose**: Identifies the high-level maintenance action required and retrieves the exact regulatory standards governing that action.
*   **Mechanism**: 
    1.  Determines the broad action (e.g., "Foundation Underpinning").
    2.  Instantiates `GoogleGenerativeAIEmbeddings`.
    3.  Queries the local `ChromaDB` vector store using the `crack_type` as the query.
    4.  Extracts the most relevant chunks from the `knowledge_base.txt` and appends them to the graph state as `rag_context`.
*   **Why**: This is the crucial step that prevents AI hallucination. By pulling actual textbook/regulatory clauses, we force the downstream LLM to abide by real-world engineering standards.

### Node 5: Resource Optimization (`Agent5_Resources`)
*   **Purpose**: Calculates the logistics required for the maintenance plan.
*   **Mechanism**: Deterministically assigns `required_workers`, arrays of `required_materials` (e.g., High-strength concrete, Rebar), and an `estimated_cost`.

### Node 6: LLM Recommendation (`Agent6_LLM`)
*   **Purpose**: Synthesizes the entire state (Scores, Materials, RAG Context) into a professional, human-readable executive summary.
*   **Mechanism**: Constructs a strict prompt injecting the `rag_context` retrieved by Agent 4. It commands the Gemini Flash model to draft a 3-part report:
    1.  Executive Summary
    2.  Regulatory Compliance & Justification (citing the RAG context)
    3.  Resource Allocation
*   **Why**: Human engineers and stakeholders need easily digestible reports. The LLM translates the raw data and standards into a coherent, persuasive document for immediate approval.

---

## 4. The Retrieval-Augmented Generation (RAG) Pipeline

To implement the RAG pipeline, the system utilizes an ingestion script (`scripts/init_db.py`):
1.  **Loading**: Reads `backend/data/knowledge_base.txt` (a mock document containing strict regulatory clauses for things like Foundation Settlement and Spalling).
2.  **Splitting**: Uses Langchain's `RecursiveCharacterTextSplitter` to break the document into smaller, semantically meaningful chunks (500 characters each).
3.  **Embedding**: Passes the chunks to `gemini-embedding-2`, converting the text into high-dimensional vectors representing their semantic meaning.
4.  **Storage**: Saves these vectors persistently to the local filesystem in the `chroma_db/` directory.

When the API is hit, Agent 4 takes the user's `crack_type`, embeds it, and asks ChromaDB to find the vectors that are closest mathematically. The text associated with those vectors is then passed to Agent 6.

---

## 5. Summary & Real-World Application

CivilCortex successfully demonstrates a **Deterministic-Generative Hybrid Architecture**. By restricting the LLM exclusively to the final synthesis step (Agent 6) and forcing it to rely on retrieved context (Agent 4), the project completely mitigates the risks of hallucination common in naive AI applications. 

This makes CivilCortex a highly viable architecture for real-world publication and deployment in the Civil Engineering tech sector, where accuracy and compliance are paramount.
