from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.core.database import get_db

router = APIRouter()

@router.get("/users")
def read_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    users = db.query(User).offset(skip).limit(limit).all()
    # Masking hashed_password for security
    for u in users:
        u.hashed_password = None
    return users

@router.post("/users/{user_id}/suspend")
def suspend_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user),
) -> Any:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.add(user)
    db.commit()
    return {"message": f"User {user_id} suspended successfully"}
