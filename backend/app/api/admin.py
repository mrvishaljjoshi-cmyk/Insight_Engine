from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User, UserRole
from app.core.database import get_db
from app.core.security import get_password_hash
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    mobile_no: str = None
    role: UserRole = UserRole.Trader

@router.get("/users")
def read_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/users")
def create_user_admin(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user),
) -> Any:
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username exists")
    
    user = User(
        username=user_in.username,
        email=user_in.email,
        mobile_no=user_in.mobile_no,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/pending-updates")
def get_pending_updates(
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user)
) -> Any:
    """Get all users with pending profile updates"""
    users = db.query(User).filter(User.pending_profile_update != None).all()
    return [
        {
            "user_id": u.id,
            "username": u.username,
            "pending": u.pending_profile_update,
            "current": {
                "email": u.email,
                "mobile_no": u.mobile_no,
                "telegram_id": u.telegram_id,
                "linked_gmail": u.linked_gmail
            }
        } for u in users
    ]

@router.post("/users/{user_id}/approve-update")
def approve_update(
    user_id: int,
    approve: bool = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user)
) -> Any:
    """Approve or Reject a pending profile update"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.pending_profile_update:
        raise HTTPException(status_code=404, detail="No pending update found")
    
    if approve:
        pending = user.pending_profile_update
        if "email" in pending: user.email = pending["email"]
        if "mobile_no" in pending: user.mobile_no = pending["mobile_no"]
        if "telegram_id" in pending: user.telegram_id = pending["telegram_id"]
        if "linked_gmail" in pending: user.linked_gmail = pending["linked_gmail"]
        message = "Update approved and applied"
    else:
        message = "Update rejected"
        
    user.pending_profile_update = None
    db.commit()
    return {"message": message}
