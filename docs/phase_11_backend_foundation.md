# Phase 11: Backend Foundation

This document describes the foundational CivilCortex backend setup, which leverages FastAPI and PostgreSQL. The application relies entirely on clean domain principles where ML output strictly serves as `DEVELOPMENT` insight rather than production engineering assertions.

## Setup & Environment

The backend consumes the following environment variables:
- `DATABASE_URL`: The PostgreSQL connection string (defaults to `postgresql://civilcortex:civilcortex@localhost/civilcortex`).
- `TEST_DATABASE_URL`: Connection string for running test suites (defaults to `sqlite:///./test.db`).
- `SECRET_KEY`: Used for signing JWT access tokens.
- `STORAGE_ROOT`: Relative path from the project root for local file storage (defaults to `storage/images/`).

## Database Initialization and Migrations

Migrations are powered by Alembic:

To generate a new migration after model changes:
```bash
cd backend
../.venv/bin/alembic revision --autogenerate -m "Migration message"
```

To upgrade a fresh database:
```bash
cd backend
../.venv/bin/alembic upgrade head
```

## API Structure

The API conforms to the hierarchical design required for defect localization:

### Authentication
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Structural Hierarchy
- `POST /api/v1/buildings` & `GET /api/v1/buildings`
- `POST /api/v1/floors`
- `POST /api/v1/areas`
- `POST /api/v1/structural-elements`

### Inspections & Media
- `POST /api/v1/inspections/` & `GET /api/v1/inspections/`
- `POST /api/v1/inspections/{inspection_id}/images`
- `POST /api/v1/inspections/{inspection_id}/images/{image_id}/analyze`

### Defects & Assessments
- `POST /api/v1/defects/` & `PUT /api/v1/defects/{defect_id}`
- `POST /api/v1/defects/observations`
- `POST /api/v1/defects/observations/{observation_id}/assessments`

## Image Storage

All uploaded images are validated for size and MIME types (`image/jpeg`, `image/png`, `image/webp`). They are persisted to disk locally in the project root under the `storage/images/` directory. Only absolute system paths are stored within the PostgreSQL instance.

## ML Service Abstraction

The ML capabilities remain in the `DEVELOPMENT` phase. The `MLService` abstraction exposes an `analyze_image(image_path)` function which yields deterministic classifications explicitly flagged as `DEVELOPMENT` to prevent misinterpretation of production capability. 

## Testing

The backend implements the core FastAPI `TestClient` suite for integration validation (Auth, Hierarchy construction, ML abstraction integration).

```bash
cd backend
PYTHONPATH=. ../.venv/bin/pytest tests/test_api.py -v
```

## Starting the Backend

To start the backend in development mode:

```bash
cd backend
../.venv/bin/uvicorn app.main:app --reload
```
