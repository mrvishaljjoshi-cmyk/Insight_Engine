"""
Insight Engine - FastAPI Backend Application

Professional Indian Trading Platform API providing:
    - JWT-based authentication
    - Multi-broker integration (Zerodha, Angel One, Groww, Dhan, Upstox)
    - Real-time market data via WebSocket
    - Secure credential storage with Fernet encryption

Architecture:
    - FastAPI with SQLAlchemy ORM
    - PostgreSQL/SQLite database
    - Redis for sessions and caching
    - Rate limiting with slowapi
    - CORS protection

Security:
    - JWT tokens (HS256, 30min expiry)
    - bcrypt password hashing (12 rounds)
    - Fernet credential encryption
    - Rate limiting on auth endpoints
    - CORS whitelist

Environment Variables:
    See .env.example for all configuration options.
"""
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from app.api import auth, admin, brokers, ws, holdings, ai, trades, market, admin_dashboard, signals
from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.core.security import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session
from datetime import datetime

app = FastAPI(
    title="Insight",
    description="Professional Trading Platform API",
    version="production",
    openapi_url="/openapi.json"
)

# Add limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - restrict to production domain
origins = [
    "https://insight.vjprojects.co.in",
    "https://vjprojects.co.in",
    "http://localhost:8081",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    max_age=3600,
)

from app.core.worker import signal_worker_loop
import asyncio

@app.on_event("startup")
async def startup_event():
    """Execute startup protocols: Initialize workers and neural links."""
    asyncio.create_task(signal_worker_loop())

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(admin_dashboard.router, prefix="/admin-dashboard", tags=["admin-dashboard"])
app.include_router(brokers.router, prefix="/brokers", tags=["brokers"])
app.include_router(holdings.router, prefix="/holdings", tags=["holdings"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(trades.router, prefix="/trades", tags=["trades"])
app.include_router(market.router, prefix="/market", tags=["market"])
app.include_router(signals.router, prefix="/signals", tags=["signals"])
app.include_router(ws.router, prefix="/ws", tags=["websockets"])


@app.get("/")
def root():
    return {
        "name": "Insight",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }


from app.core.redis import redis_client
from sqlalchemy import text, inspect

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check for monitoring systems"""
    health = readiness_check(db)
    return {
        "status": health["status"],
        "service": "Insight API",
        "timestamp": health["timestamp"],
        "components": health["components"]
    }


@app.get("/health/liveness")
def liveness_check():
    """Fast liveness probe for basic availability"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/readiness")
def readiness_check(db: Session = Depends(get_db)):
    """Deep readiness probe for component health"""
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "unknown",
            "redis": "unknown"
        }
    }
    
    try:
        db.execute(text("SELECT 1"))
        health["components"]["database"] = "connected"
    except Exception as e:
        health["status"] = "unhealthy"
        health["components"]["database"] = f"error: {str(e)}"

    try:
        if redis_client.ping():
            health["components"]["redis"] = "connected"
        else:
            health["status"] = "unhealthy"
            health["components"]["redis"] = "disconnected"
    except Exception as e:
        health["status"] = "unhealthy"
        health["components"]["redis"] = f"error: {str(e)}"

    return health


@app.get("/api/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}", "role": current_user.role}


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
