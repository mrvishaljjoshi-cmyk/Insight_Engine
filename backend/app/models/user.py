import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class UserRole(str, enum.Enum):
    Admin = "Admin"
    Trader = "Trader"
    Developer = "Developer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile_no = Column(String, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.Trader, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    brokers = relationship("BrokerCredential", back_populates="owner")
    watchlists = relationship("Watchlist", back_populates="owner", cascade="all, delete-orphan")


class BrokerCredential(Base):
    __tablename__ = "broker_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    broker_name = Column(String, index=True, nullable=False)
    credentials = Column(JSON, nullable=False) 
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="brokers")
    trades = relationship("TradeJournal", back_populates="broker")
