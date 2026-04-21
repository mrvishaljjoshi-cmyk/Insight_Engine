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
from app.api import auth, admin, brokers, ws
from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.core.security import get_current_user
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

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(brokers.router, prefix="/brokers", tags=["brokers"])
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
    """Enhanced health check endpoint for monitoring all components"""
    health = {
        "status": "healthy",
        "service": "insight-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "production",
        "components": {
            "database": {"status": "unknown", "details": {}},
            "redis": {"status": "unknown", "details": {}},
            "connection_pool": {"status": "unknown", "details": {}}
        }
    }

    # Check Database Connection
    try:
        db.execute(text("SELECT 1"))
        health["components"]["database"]["status"] = "connected"

        # Check tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        health["components"]["database"]["details"]["tables"] = tables

        # Check for required tables
        required_tables = ['users', 'broker_credentials', 'market_data', 'watchlists', 'trade_journal']
        missing = [t for t in required_tables if t not in tables]
        if missing:
            health["components"]["database"]["details"]["missing_tables"] = missing
            health["status"] = "degraded"
    except Exception as e:
        health["status"] = "unhealthy"
        health["components"]["database"]["status"] = f"error: {str(e)}"

    # Check Redis
    try:
        if redis_client.ping():
            health["components"]["redis"]["status"] = "connected"
            info = redis_client.info()
            health["components"]["redis"]["details"]["version"] = info.get("redis_version", "unknown")
        else:
            health["status"] = "unhealthy"
            health["components"]["redis"]["status"] = "disconnected"
    except Exception as e:
        health["status"] = "unhealthy"
        health["components"]["redis"]["status"] = f"error: {str(e)}"

    # Check Connection Pool (PostgreSQL only)
    if "postgresql" in settings.DATABASE_URL.lower():
        try:
            pool = engine.pool
            health["components"]["connection_pool"]["status"] = "active"
            health["components"]["connection_pool"]["details"] = {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "pool_class": pool.__class__.__name__
            }
        except Exception as e:
            health["components"]["connection_pool"]["status"] = f"error: {str(e)}"

    return health


@app.get("/api/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}", "role": current_user.role}


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
