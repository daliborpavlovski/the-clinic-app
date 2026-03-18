from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .routers import auth, users, appointments, doctors

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="NexusClinic — Clinic Appointment Management Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(appointments.router, prefix=API_PREFIX)
app.include_router(doctors.router, prefix=API_PREFIX)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": settings.app_name}


@app.get("/", include_in_schema=False)
def root():
    return {"message": "NexusClinic API", "docs": "/docs"}
