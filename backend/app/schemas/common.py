"""
Common Pydantic schemas shared across the application.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, Generic, TypeVar
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response schema for all API responses."""
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    total: Optional[int] = None
    total_pages: Optional[int] = None


class PaginatedResponse(BaseModel, Generic[TypeVar('T')]):
    """Generic paginated response schema."""
    data: list
    pagination: PaginationParams


class HealthCheckResponse(BaseModel):
    """Schema for health check endpoint response."""
    status: str  # "healthy", "unhealthy", "degraded"
    service: str
    timestamp: datetime
    components: Dict[str, str]
    version: Optional[str] = None


class MarketTick(BaseModel):
    """Schema for real-time market data tick."""
    symbol: str
    price: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime
    unix_timestamp: int


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""
    type: str  # "tick", "order_update", "alert", "error"
    data: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class APIStats(BaseModel):
    """Schema for API statistics."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    uptime_seconds: int