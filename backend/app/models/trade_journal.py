import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class TradeStatus(str, enum.Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class TradeType(str, enum.Enum):
    INTRADAY = "INTRADAY"
    DELIVERY = "DELIVERY"
    FNO = "FNO"


class TradeJournal(Base):
    __tablename__ = "trade_journal"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    broker_id = Column(Integer, ForeignKey("broker_credentials.id"), nullable=True)

    symbol = Column(String, index=True, nullable=False)
    exchange = Column(String, nullable=False, default="NSE")
    trade_type = Column(Enum(TradeType), nullable=False)

    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Integer, nullable=False)

    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=True)

    pnl = Column(Float, nullable=True)
    pnl_percentage = Column(Float, nullable=True)

    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING, index=True)

    strategy = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    trader = relationship("User")
    broker = relationship("BrokerCredential")