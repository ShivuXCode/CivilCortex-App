# CivilCortex: Setup and Execution Guide

## 1. Prerequisites
- **Python**: 3.11+
- **Node.js**: 20+ / 22+ / 26+ and **npm**
- **Google Gemini API Key** (Set in `backend/.env`)

---

## 2. Virtual Environment & Dependencies

CivilCortex uses a dedicated Python 3.11 virtual environment at `backend/.venv` (symlinked as `.venv` in the root).

### To activate the virtual environment:
```bash
source .venv/bin/activate
```

### To install backend dependencies:
```bash
.venv/bin/pip install -r backend/requirements.txt
```

### To install frontend dependencies:
```bash
cd frontend
npm install
```

---

## 3. Running the Project Locally

### A. Start the Backend API Server:
```bash
cd backend
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
* **API Root**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### B. Start the Frontend Application:
```bash
cd frontend
npm run dev
```
* **Web UI**: [http://localhost:5173](http://localhost:5173)

---

## 4. API Endpoints Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/register` | POST | Register a new user |
| `/api/login` | POST | Authenticate and obtain JWT access token |
| `/api/analyze-maintenance` | POST | Run deterministic 6-agent maintenance workflow |
| `/api/analyze-image` | POST | Upload an inspection image for ML & multimodal analysis |
| `/api/inspections` | GET | Retrieve user inspection records |
| `/api/export-pdf/{id}` | GET | Generate and download executive PDF report |
