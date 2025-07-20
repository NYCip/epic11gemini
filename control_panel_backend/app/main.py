from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
from sqlalchemy.orm import Session
import os
import time
from datetime import timedelta
import logging

from .database import engine, get_db
from . import models, schemas
from .auth import auth_service
from .routers import auth as auth_router, users as users_router, system as system_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.redis = await aioredis.from_url(
        os.getenv("REDIS_URL", "redis://redis:6379"),
        encoding="utf-8",
        decode_responses=True
    )
    app.state.start_time = time.time()
    logger.info("EPIC V11 Control Panel API starting up...")
    yield
    # Shutdown
    await app.state.redis.close()
    logger.info("EPIC V11 Control Panel API shutting down...")

app = FastAPI(
    title="EPIC V11 Control Panel API",
    description="Secure multi-user control panel for EPIC V11 AI System",
    version="11.0.0",
    lifespan=lifespan
)

# CORS configuration for epic.pos.com
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://epic.pos.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/control/auth", tags=["Authentication"])
app.include_router(users_router.router, prefix="/control/users", tags=["Users"])
app.include_router(system_router.router, prefix="/control/system", tags=["System Control"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "control_panel_backend"}

@app.get("/")
async def root():
    return {
        "service": "EPIC V11 Control Panel API",
        "status": "operational",
        "documentation": "https://epic.pos.com/docs"
    }

# Audit logging middleware
@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    # Skip logging for health checks
    if request.url.path == "/health":
        return await call_next(request)
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log request (implement based on your needs)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response
