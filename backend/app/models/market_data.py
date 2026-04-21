from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base


class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    exchange = Column(String, index=True, nullable=False, default="NSE")
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    last_price = Column(Float, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_market_data_symbol_exchange', 'symbol', 'exchange'),
        Index('ix_market_data_timestamp', 'timestamp'),
    )