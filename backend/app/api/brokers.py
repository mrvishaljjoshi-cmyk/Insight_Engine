from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import (
    get_current_user,
    encrypt_credentials,
    decrypt_credentials,
    mask_credentials
)
from app.models.user import User, BrokerCredential
from app.services.broker_factory import BrokerFactory

router = APIRouter()


class BrokerCreate(BaseModel):
    broker_name: str
    credentials: Dict[str, Any]


class BrokerResponse(BaseModel):
    id: int
    broker_name: str
    is_active: bool
    credentials: Dict[str, Any]

    class Config:
        from_attributes = True


class BrokerInternal(BaseModel):
    id: int
    broker_name: str
    is_active: bool
    credentials: Dict[str, Any]

    class Config:
        from_attributes = True


@router.post("/", response_model=BrokerResponse)
def add_broker(
    broker: BrokerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new broker connection for the authenticated user"""
    # Encrypt credentials before storing
    encrypted_creds = encrypt_credentials(broker.credentials)

    db_broker = BrokerCredential(
        user_id=current_user.id,
        broker_name=broker.broker_name,
        credentials=encrypted_creds
    )
    db.add(db_broker)
    db.commit()
    db.refresh(db_broker)

    # Return with masked credentials
    return {
        "id": db_broker.id,
        "broker_name": db_broker.broker_name,
        "is_active": db_broker.is_active,
        "credentials": mask_credentials(broker.credentials)
    }


@router.get("/", response_model=List[BrokerResponse])
def get_brokers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all broker connections for the authenticated user"""
    brokers = db.query(BrokerCredential).filter(
        BrokerCredential.user_id == current_user.id
    ).all()

    # Return with masked credentials
    result = []
    for broker in brokers:
        try:
            decrypted = decrypt_credentials(broker.credentials)
            masked = mask_credentials(decrypted)
        except Exception:
            masked = {"error": "Failed to decrypt"}

        result.append({
            "id": broker.id,
            "broker_name": broker.broker_name,
            "is_active": broker.is_active,
            "credentials": masked
        })

    return result


@router.get("/{broker_id}", response_model=BrokerResponse)
def get_broker(
    broker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific broker connection"""
    broker = db.query(BrokerCredential).filter(
        BrokerCredential.id == broker_id,
        BrokerCredential.user_id == current_user.id
    ).first()

    if not broker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker not found"
        )

    try:
        decrypted = decrypt_credentials(broker.credentials)
        masked = mask_credentials(decrypted)
    except Exception:
        masked = {"error": "Failed to decrypt"}

    return {
        "id": broker.id,
        "broker_name": broker.broker_name,
        "is_active": broker.is_active,
        "credentials": masked
    }


@router.delete("/{broker_id}")
def delete_broker(
    broker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a broker connection"""
    db_broker = db.query(BrokerCredential).filter(
        BrokerCredential.id == broker_id,
        BrokerCredential.user_id == current_user.id
    ).first()

    if not db_broker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker not found"
        )

    db.delete(db_broker)
    db.commit()
    return {"message": "Broker disconnected successfully"}


@router.patch("/{broker_id}/toggle")
def toggle_broker(
    broker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle broker active status"""
    db_broker = db.query(BrokerCredential).filter(
        BrokerCredential.id == broker_id,
        BrokerCredential.user_id == current_user.id
    ).first()

    if not db_broker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker not found"
        )

    db_broker.is_active = not db_broker.is_active
    db.commit()

    return {
        "message": f"Broker {'activated' if db_broker.is_active else 'deactivated'}",
        "is_active": db_broker.is_active
    }


@router.get("/{broker_id}/holdings")
def get_broker_holdings(
    broker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch live holdings from the broker"""
    db_broker = db.query(BrokerCredential).filter(
        BrokerCredential.id == broker_id,
        BrokerCredential.user_id == current_user.id
    ).first()

    if not db_broker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker connection not found"
        )

    try:
        broker_instance = BrokerFactory.get_broker(
            db_broker.broker_name, 
            db_broker.credentials,
            user_id=current_user.id
        )
        return broker_instance.get_holdings()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch holdings: {str(e)}"
        )
