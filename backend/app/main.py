from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, hierarchy, inspections, defects

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(hierarchy.router, prefix=f"{settings.API_V1_STR}", tags=["hierarchy"])
app.include_router(inspections.router, prefix=f"{settings.API_V1_STR}/inspections", tags=["inspections"])
app.include_router(defects.router, prefix=f"{settings.API_V1_STR}/defects", tags=["defects"])

@app.get("/")
def root():
    return {"message": "Welcome to CivilCortex API"}
