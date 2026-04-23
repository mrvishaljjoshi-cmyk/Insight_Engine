import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class PlanType(str, enum.Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    PRO = "PRO"
    ULTIMATE = "ULTIMATE"

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(PlanType), unique=True, index=True)
    price = Column(Float, nullable=False)
    features = Column(JSON) # Structured list of feature toggles
    duration_days = Column(Integer, default=30)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    expiry_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    plan = relationship("SubscriptionPlan")
    user = relationship("User", back_populates="subscription")
