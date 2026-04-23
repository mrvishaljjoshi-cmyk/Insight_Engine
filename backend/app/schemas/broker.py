"""
Pydantic schemas for broker management and operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class BrokerName(str, Enum):
    """Supported broker names."""
    ZERODHA = "Zerodha"
    ANGEL_ONE = "Angel One"
    GROWW = "Groww"
    DHAN = "Dhan"
    UPSTOX = "Upstox"


class BrokerCredentials(BaseModel):
    """Schema for broker credentials (base for input)."""
    # Zerodha
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    client_id: Optional[str] = None
    totp_secret: Optional[str] = None
    access_token: Optional[str] = None

    # Angel One specific
    smartapi_key: Optional[str] = None
    password: Optional[str] = None

    class Config:
        extra = "allow"


class BrokerCreate(BaseModel):
    """Schema for creating a broker connection."""
    broker_name: str = Field(..., min_length=1)
    credentials: Dict[str, Any]


class BrokerUpdate(BaseModel):
    """Schema for updating broker credentials."""
    credentials: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class BrokerResponse(BaseModel):
    """Schema for broker response (masked credentials)."""
    id: int
    broker_name: str
    is_active: bool
    credentials: Dict[str, Any]  # Masked
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BrokerDetail(BaseModel):
    """Schema for detailed broker information."""
    id: int
    broker_name: str
    is_active: bool
    connection_status: str  # "connected", "disconnected", "error"
    last_sync: Optional[datetime] = None


class BrokerStatus(BaseModel):
    """Schema for broker connection status check."""
    broker_id: int
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class HoldingsItem(BaseModel):
    """Schema for a single holding item."""
    symbol: str
    quantity: int
    average_price: float
    current_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None


class HoldingsResponse(BaseModel):
    """Schema for holdings response."""
    broker_name: str
    holdings: List[HoldingsItem]
    total_value: float
    total_pnl: float


class PositionItem(BaseModel):
    """Schema for a single position item."""
    symbol: str
    quantity: int
    side: str  # "BUY" or "SELL"
    average_price: float
    current_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None


class PositionsResponse(BaseModel):
    """Schema for positions response."""
    broker_name: str
    positions: List[PositionItem]
    total_pnl: float


class OrderItem(BaseModel):
    """Schema for a single order item."""
    order_id: str
    symbol: str
    side: str
    quantity: int
    price: Optional[float] = None
    order_type: str  # "MARKET", "LIMIT", "SL"
    status: str  # "OPEN", "COMPLETED", "CANCELLED", "REJECTED"
    created_at: datetime


class OrdersResponse(BaseModel):
    """Schema for orders response."""
    broker_name: str
    orders: List[OrderItem]


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOPLOSS = "SL"
    STOPLOSS_MARKET = "SL-M"


class OrderCreate(BaseModel):
    """Schema for placing a new order."""
    symbol: str = Field(..., description="Trading symbol (e.g., NIFTY24JANFUT)")
    quantity: int = Field(..., gt=0, description="Order quantity")
    side: OrderSide = Field(..., description="Buy or Sell")
    order_type: OrderType = Field(..., description="Market, Limit, or Stoploss")
    price: Optional[float] = Field(None, ge=0, description="Limit/SL price (required for LIMIT/SL orders)")
    product: str = Field(default="MIS", description="Product type: MIS, NRML, CNC, BO, CO")
    validity: str = Field(default="DAY", description="Order validity: DAY or IOC")