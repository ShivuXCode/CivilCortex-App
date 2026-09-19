import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, hierarchy, inspections, defects, analysis
from app.core.logger import logger, request_id_var
from app.core.exceptions import CivilCortexError

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

from contextlib import asynccontextmanager
from sqlalchemy import text
from app.db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify database connectivity on startup
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connectivity verified.")
    except Exception as e:
        logger.error(f"Failed to connect to the database on startup: {e}")
        raise RuntimeError("Startup failed: Database unreachable")
        
    yield
    
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    req_id = str(uuid.uuid4())
    request_id_var.set(req_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response

@app.exception_handler(CivilCortexError)
async def civil_cortex_exception_handler(request: Request, exc: CivilCortexError):
    logger.warning(f"Domain error {exc.code}: {exc.message}")
    
    # Map domain errors to HTTP status codes
    status_mapping = {
        "VALIDATION_ERROR": 400,
        "AUTHENTICATION_ERROR": 401,
        "AUTHORIZATION_ERROR": 403,
        "NOT_FOUND": 404,
        "STORAGE_ERROR": 500,
        "IMAGE_PROCESSING_ERROR": 400,
        "CV_INFERENCE_ERROR": 500,
        "RAG_ERROR": 500,
        "LLM_ERROR": 500,
        "DATABASE_ERROR": 500,
        "QUEUE_ERROR": 500,
        "INTERNAL_ERROR": 500,
    }
    status_code = status_mapping.get(exc.code, 500)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id_var.get()
            }
        }
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": request_id_var.get()
            }
        }
    )

# CORS — scoped to only the methods and headers the frontend actually uses.
# Using allow_methods=["*"] and allow_headers=["*"] in production is a security
# risk as it allows arbitrary cross-origin requests with any method or header.
is_production = settings.ENVIRONMENT == "production"
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    # In production, restrict to only the methods the API actually exposes.
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"] if is_production else ["*"],
    # In production, restrict to only the headers the frontend sends.
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"] if is_production else ["*"],
)

# Include Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(hierarchy.router, prefix=f"{settings.API_V1_STR}", tags=["hierarchy"])
app.include_router(inspections.router, prefix=f"{settings.API_V1_STR}/inspections", tags=["inspections"])
app.include_router(defects.router, prefix=f"{settings.API_V1_STR}/defects", tags=["defects"])
app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["analysis"])

@app.get("/")
def root():
    return {"message": "Welcome to CivilCortex API"}
