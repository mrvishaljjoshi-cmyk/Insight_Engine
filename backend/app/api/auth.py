from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.user import User, UserRole

router = APIRouter()

class LoginSchema(BaseModel):
    email: str
    password: str

class GoogleAuthSchema(BaseModel):
    token: str

@router.post("/auth/login")
def login_auth(
    db: Session = Depends(get_db), data: LoginSchema = Body(...)
) -> Any:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "role": user.role,
        "token_type": "bearer",
    }

@router.post("/auth/google")
def auth_google(
    db: Session = Depends(get_db), data: GoogleAuthSchema = Body(...)
) -> Any:
    try:
        idinfo = id_token.verify_oauth2_token(data.token, requests.Request(), settings.GOOGLE_CLIENT_ID)
        email = idinfo['email']
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Auto-register user
            user = User(
                email=email,
                role=UserRole.Trader,
                is_active=True,
                hashed_password=None
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "token": create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "role": user.role,
            "token_type": "bearer",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
