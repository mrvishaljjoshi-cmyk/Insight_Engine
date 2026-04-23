from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Index, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, unique=True, nullable=False)
    company_name = Column(String, nullable=True)
    exchange = Column(String, index=True, nullable=False, default="NSE")
    last_price = Column(Float, nullable=True)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    prev_close = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AlphaSignal(Base):
    __tablename__ = "alpha_signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    segment = Column(String, default="STOCK") # STOCK, OPTION, MCX
    signal_type = Column(String) # BULLISH_BREAKOUT, VOL_SPIKE
    entry_price = Column(Float)
    target = Column(Float)
    stop_loss = Column(Float)
    strength = Column(Integer) # 1-100
    narrative = Column(String)
    is_active = Column(Boolean, default=True)
    status = Column(String, default="OPEN") # OPEN, TARGET_HIT, SL_HIT, CLOSED
    exit_price = Column(Float, nullable=True)
    profit_loss = Column(Float, nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())