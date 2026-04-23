from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole, BrokerCredential
from app.models.subscription import Subscription, SubscriptionPlan, PlanType
from app.core.database import get_db
from app.core.security import get_current_user
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta

router = APIRouter()

# Helper dependency for Admin check
def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.Admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    return current_user

class PlanCreate(BaseModel):
    name: PlanType
    price: float
    features: Dict[str, bool]
    duration_days: int = 30

class UserSubscriptionUpdate(BaseModel):
    plan_id: int
    is_active: bool = True

class ProfileApproval(BaseModel):
    approve: bool

@router.get("/pending-updates")
def list_pending_updates(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    users = db.query(User).filter(User.pending_profile_update != None).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "pending_updates": u.pending_profile_update
        } for u in users
    ]

@router.post("/users/{user_id}/approve-profile")
def approve_profile_update(
    user_id: int,
    data: ProfileApproval,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.pending_profile_update:
        raise HTTPException(status_code=404, detail="No pending updates found for this user")
    
    if data.approve:
        pending = user.pending_profile_update
        if "username" in pending: user.username = pending["username"]
        if "email" in pending: user.email = pending["email"]
        if "mobile_no" in pending: user.mobile_no = pending["mobile_no"]
        if "telegram_id" in pending: user.telegram_id = pending["telegram_id"]
        if "linked_gmail" in pending: user.linked_gmail = pending["linked_gmail"]
        message = "Profile update approved"
    else:
        message = "Profile update rejected"
        
    user.pending_profile_update = None
    db.commit()
    return {"message": message}

@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    total_users = db.query(User).count()
    active_brokers = db.query(BrokerCredential).filter(BrokerCredential.is_active == True).count()
    total_revenue = 0.0 # Logic to sum from a hypothetical payments table
    
    return {
        "total_users": total_users,
        "active_brokers": active_brokers,
        "active_subscriptions": db.query(Subscription).filter(Subscription.is_active == True).count()
    }

@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "brokers_count": len(u.brokers),
            "subscription": {
                "plan": u.subscription.plan.name if u.subscription else "NONE",
                "expiry": u.subscription.expiry_date if u.subscription else None
            } if u.subscription else None
        } for u in users
    ]

@router.get("/plans")
def list_plans(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    return db.query(SubscriptionPlan).all()

@router.post("/plans")
def create_plan(
    plan_in: PlanCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    existing = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == plan_in.name).first()
    if existing:
        existing.price = plan_in.price
        existing.features = plan_in.features
        existing.duration_days = plan_in.duration_days
        db.commit()
        return existing
    
    plan = SubscriptionPlan(**plan_in.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.post("/users/{user_id}/subscription")
def update_user_subscription(
    user_id: int,
    data: UserSubscriptionUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == data.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not sub:
        sub = Subscription(user_id=user_id)
        db.add(sub)
    
    sub.plan_id = plan.id
    sub.is_active = data.is_active
    sub.start_date = datetime.utcnow()
    sub.expiry_date = datetime.utcnow() + timedelta(days=plan.duration_days)
    
    db.commit()
    return {"message": f"User {user.username} subscription updated to {plan.name}"}

@router.get("/users/{user_id}/brokers")
def list_user_brokers(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    brokers = db.query(BrokerCredential).filter(BrokerCredential.user_id == user_id).all()
    # Mask credentials for admin view
    return [
        {
            "id": b.id,
            "broker_name": b.broker_name,
            "is_active": b.is_active,
            "created_at": b.created_at
        } for b in brokers
    ]
