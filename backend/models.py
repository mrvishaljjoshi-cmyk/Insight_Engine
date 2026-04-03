from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    telegram_id = Column(String, nullable=True)
    is_email_verified = Column(Boolean, default=False)
    is_telegram_verified = Column(Boolean, default=False)
    ai_refresh_count = Column(Integer, default=0)
    last_refresh_date = Column(DateTime, nullable=True)
    is_subscribed = Column(Boolean, default=False)
    subscription_expiry = Column(DateTime, nullable=True)
    brokers = relationship("Broker", back_populates="owner")
    snapshots = relationship("PortfolioSnapshot", back_populates="owner")

class Broker(Base):
    __tablename__ = "brokers"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String) 
    client_code = Column(String)
    api_key = Column(String)
    api_secret = Column(String) # For the ab8982... key
    totp_secret = Column(String, nullable=True)
    pin = Column(String, nullable=True)
    access_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="brokers")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    broker_id = Column(Integer, ForeignKey("brokers.id"))
    symbol = Column(String)
    transaction_type = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    order_id = Column(String, unique=True)

class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON)
    total_value = Column(Float)
    ai_summary = Column(String, nullable=True)
    owner = relationship("User", back_populates="snapshots")
