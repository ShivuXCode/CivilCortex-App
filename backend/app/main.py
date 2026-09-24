import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import analyses
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
        from app.models.analysis import Analysis
        from app.db.base import Base
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connectivity verified and schema created.")
    except Exception as e:
        logger.error(f"Failed to connect to the database on startup: {e}")
        raise RuntimeError("Startup failed: Database unreachable")
        
    import asyncio
    from app.worker import reap_stale_jobs
    
    async def periodic_reaper():
        while True:
            # Run every 5 minutes
            await asyncio.sleep(300)
            await asyncio.to_thread(reap_stale_jobs)

    reaper_task = asyncio.create_task(periodic_reaper())
    
    yield
    
    reaper_task.cancel()
    
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
    return JSONResponse(
        status_code=500,
        content={"error": {"code": exc.code, "message": exc.message, "request_id": request_id_var.get()}}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred.", "request_id": request_id_var.get()}}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(analyses.router, prefix=f"{settings.API_V1_STR}/analyses", tags=["analyses"])

@app.get("/")
def root():
    return {"message": "Welcome to CivilCortex API"}
