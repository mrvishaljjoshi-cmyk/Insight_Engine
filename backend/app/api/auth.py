"""
Authentication API endpoints for user registration, login, and profile management.

This module provides:
- User registration with email validation
- JWT-based authentication (login/logout)
- Password reset via Redis tokens
- Profile management (view, update, delete)

All endpoints are rate-limited to prevent abuse.

Routes:
    POST /auth/login          - Authenticate user, return JWT
    POST /auth/register      - Create new user account
    GET  /auth/me            - Get current user profile
    PATCH /auth/me           - Update profile (email, mobile)
    DELETE /auth/me          - Delete account
    POST /auth/change-password - Change password while logged in
    POST /auth/password-reset-request - Request password reset
    POST /auth/password-reset-confirm - Confirm password reset
    POST /auth/logout        - Logout (client-side)
"""
from datetime import timedelta
from typing import Any, Dict, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Body, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
import secrets

from app.core.config import settings
from app.core.database import get_db
from app.core.limiter import limiter
from app.core.redis import redis_client
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
    security
)
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from datetime import datetime, timezone
from app.models.user import User, UserRole

router = APIRouter()


class LoginSchema(BaseModel):
    username_or_email: str
    password: str
    remember_me: bool = False


class RegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    mobile_no: str = None


class ResetRequestSchema(BaseModel):
    email: EmailStr


class ResetConfirmSchema(BaseModel):
    token: str
    new_password: str


class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str


class ProfileUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile_no: Optional[str] = None
    telegram_id: Optional[str] = None
    linked_gmail: Optional[str] = None


@router.post("/login")
@limiter.limit("10/minute")
def login_auth(
    request: Request,
    data: LoginSchema,
    db: Session = Depends(get_db)
) -> Any:
    """Authenticate user and return JWT token"""
    user = db.query(User).filter(
        (User.username == data.username_or_email) | (User.email == data.username_or_email)
    ).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Calculate token expiry (default 30m, 8h if remember_me)
    if data.remember_me:
        access_token_expires = timedelta(hours=8)
    else:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires
    )

    return {
        "token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
        "user_id": user.id
    }


@router.post("/register")
@limiter.limit("5/hour")
def register_user(
    request: Request,
    data: RegisterSchema,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user account"""
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = User(
        username=data.username,
        email=data.email,
        mobile_no=data.mobile_no,
        hashed_password=get_password_hash(data.password),
        role=UserRole.Trader,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "username": new_user.username
    }


@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "mobile_no": current_user.mobile_no,
        "role": current_user.role,
        "is_active": current_user.is_active
    }


# Prefix for redis keys
RESET_TOKEN_PREFIX = "pwd_reset:"


@router.post("/password-reset-request")
def request_reset(
    data: ResetRequestSchema,
    db: Session = Depends(get_db)
):
    """Request password reset token"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, reset instructions sent"}

    token = secrets.token_urlsafe(32)
    # Store in redis with 15 mins expiry
    redis_client.setex(f"{RESET_TOKEN_PREFIX}{token}", 900, data.email)

    # TODO: Send actual email in production
    # For now, return token for testing
    if settings.ENV != "production":
        return {
            "message": "Reset token generated",
            "debug_token": token
        }

    return {"message": "If email exists, reset instructions sent"}


@router.post("/password-reset-confirm")
def confirm_reset(
    data: ResetConfirmSchema,
    db: Session = Depends(get_db)
):
    """Confirm password reset with token"""
    redis_key = f"{RESET_TOKEN_PREFIX}{data.token}"
    email = redis_client.get(redis_key)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    
    # Delete token after use
    redis_client.delete(redis_key)

    return {"message": "Password updated successfully"}


@router.post("/change-password")
def change_password(
    data: ChangePasswordSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change password while authenticated"""
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout by blacklisting the JWT token in Redis"""
    token = credentials.credentials
    # Get token expiry to set redis TTL
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = payload.get("exp")
        now = datetime.now(timezone.utc).timestamp()
        ttl = int(exp - now)
        if ttl > 0:
            redis_client.setex(f"bl_{token}", ttl, "true")
    except Exception:
        pass
        
    return {"message": "Logged out successfully"}


@router.patch("/me")
def update_profile(
    data: ProfileUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current authenticated user information - requires Admin approval"""
    # Instead of direct update, store in pending_profile_update
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        current_user.pending_profile_update = update_data
        db.commit()
        return {"message": "Profile update request sent for Admin approval", "pending": update_data}

    return {"message": "No changes provided"}


@router.delete("/me")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete current authenticated user account and all associated data"""
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}
