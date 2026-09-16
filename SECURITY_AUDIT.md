# CivilCortex Security Audit

## Executive Summary
This audit reviews the current security posture of the CivilCortex application based on an inspection of the source code, infrastructure configuration, and product design. The application exhibits several fundamental security mechanisms (JWT authentication, role-based database ownership checks, file upload validation), but contains critical architectural flaws in access control, hardcoded secrets, and LLM usage.

## Security Posture
The application is currently in a proof-of-concept / development stage. It relies heavily on implicit ownership checks rather than explicit Role-Based Access Control (RBAC). It properly restricts file uploads by MIME type and size, but stores passwords without sufficient complexity checks. 

## Critical Findings
- **Broken Access Control on Inspections and Defects:** Ownership is validated by checking if `current_user.id == building.owner_id` or `current_user.id == inspection.inspector_id` in `backend/app/api/routes/inspections.py`. This prevents cross-tenant access, but fundamentally breaks collaboration. Engineers cannot review defects created by Inspectors unless they share the same account or building ownership, which defeats the product's split role design.
- **Hardcoded Infrastructure Credentials:** `docker-compose.yml` contains hardcoded credentials for Postgres (`postgresql://civilcortex:password@db:5432/civilcortex`) and MinIO (`minioadmin:minioadmin`).

## High Findings
- **Prompt Injection via RAG (Poisoning):** The LLM prompt in `backend/app/agents/nodes/agent6_llm.py` blindly trusts the `rag_context` injected into the prompt. If malicious content is injected into the ChromaDB, it could command the LLM to hallucinate outputs or output specific adversarial responses.
- **Missing Password Complexity Enforcement:** `backend/app/schemas/user.py` accepts any string for a password during registration. Passwords are hashed using bcrypt, but weak passwords can be trivially created.

## Medium Findings
- **Fallback Ownership Authorization Flaw:** In `backend/app/api/routes/defects.py`, `update_assessment` falls back to `assessment.observation.inspection.building.owner_id` if no structural element exists. This complex traversal increases the risk of IDOR or logic bypasses if the relational graph becomes disconnected or orphan records are left behind.
- **Lack of Model Output Sanitization:** The AI-generated markdown is pushed directly to the database. While the frontend uses `react-markdown` to safely render it (mitigating XSS), the backend itself does not sanitize the LLM output before storage.

## Low Findings
- **JWT Secret and Expiry Configuration:** `backend/app/core/security.py` creates JWTs with an expiration, but the secret key is likely hardcoded in development config or defaults.

## Authentication
Status: CONFIRMED
Location: `backend/app/core/security.py`, `backend/app/api/deps.py`
Evidence: Authentication is handled via OAuth2PasswordBearer and JWT tokens. Passwords are hashed using `passlib` (bcrypt). Token extraction and signature verification work correctly.

## Authorization
Status: CONFIRMED
Location: `backend/app/models/hierarchy.py`, `backend/app/api/routes/defects.py`
Evidence: Authorization is enforced via manual SQLAlchemy filters acting as an ownership model. There is no concept of "Roles" (Admin, Engineer, Inspector) in the `User` model, meaning the system cannot differentiate between an Inspector uploading an image and an Engineer modifying the final assessment.

## API Security
Status: INFERRED
Location: `backend/app/api/deps.py`
Evidence: Routes generally require `current_user: User = Depends(get_current_user)`. However, the FastAPI application itself has no global rate limiting, leaving it open to DoS or brute force.

## File / Object Storage Security
Status: CONFIRMED
Location: `backend/app/services/image_service.py`
Evidence: `ImageService.save_image` securely restricts file uploads to specific MIME types (`image/jpeg`, `image/png`, `image/webp`) and enforces a 20MB file size limit. It safely stores the images in MinIO.

## AI / LLM Security
Status: CONFIRMED
Location: `backend/app/agents/nodes/agent6_llm.py`
Evidence: The Gemini integration executes prompts that blindly trust the structural context and RAG context. The backend correctly catches exceptions for missing credentials or rate limits and fails gracefully. However, the prompt is vulnerable to injection if the underlying RAG documents are untrusted.

## Frontend Security
Status: CONFIRMED
Location: `frontend/src/pages/Report.tsx`
Evidence: The frontend securely handles the LLM output using `react-markdown`, successfully preventing XSS from the Markdown content.

## Infrastructure Security
Status: CONFIRMED
Location: `docker-compose.yml`
Evidence: Docker compose relies heavily on default, insecure credentials. Ports for Postgres (5433), Redis (6379), and MinIO (9000/9001) are exposed to the host machine.

## Dependency Security
Status: CONFIRMED
Location: Backend test logs
Evidence: Legacy or unmaintained package versions exist, as evidenced by Python warnings (urllib3/OpenSSL compatibility, Langchain pending deprecations, and Python 3.9 EOL notices).

## Logging / Data Exposure
Status: CONFIRMED
Location: `backend/app/agents/nodes/agent6_llm.py`
Evidence: Error handling gracefully catches API errors and returns standardized JSON strings rather than crashing, preventing severe stack trace leakage to the client.

## Production Security Gaps
The application is not ready for production from a security standpoint due to the lack of RBAC, hardcoded infrastructure credentials, and missing application-level rate limits.

# TOP SECURITY PRIORITIES
1. Implement proper RBAC in the `User` model to distinguish Engineers, Inspectors, and Admins.
2. Refactor authorization to allow Engineers to review Inspections they did not create.
3. Remove hardcoded credentials from `docker-compose.yml` and use external environment variables.
4. Implement application-level rate limiting on the FastAPI routes.
