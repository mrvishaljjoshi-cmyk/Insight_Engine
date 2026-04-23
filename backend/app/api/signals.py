from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Dict, Any
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.market_data import AlphaSignal

router = APIRouter()

@router.get("/")
def get_active_signals(
    segment: str = "STOCK",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch recent high-momentum signals filtered by segment"""
    from datetime import datetime, timedelta
    from app.services.signal_generator import generate_mock_signals
    
    # Standardize segment name
    segment = segment.upper()
    
    signals = db.query(AlphaSignal).filter(
        AlphaSignal.is_active == True,
        AlphaSignal.segment == segment,
        AlphaSignal.created_at >= datetime.now() - timedelta(hours=6)
    ).order_by(desc(AlphaSignal.created_at)).limit(10).all()
    
    # If no signals found, generate fresh ones (for demo/reliability)
    if not signals:
        generate_mock_signals(db)
        signals = db.query(AlphaSignal).filter(
            AlphaSignal.is_active == True,
            AlphaSignal.segment == segment
        ).order_by(desc(AlphaSignal.created_at)).limit(10).all()
    
    return signals

@router.get("/accuracy")
def get_signal_accuracy(db: Session = Depends(get_db)):
    """Calculate actual accuracy score from closed signals"""
    total = db.query(AlphaSignal).filter(AlphaSignal.status != "OPEN").count()
    if total == 0:
        return {"accuracy_pct": 0, "total_calls": 0, "profitable_calls": 0, "avg_profit_pct": 0}
        
    wins = db.query(AlphaSignal).filter(AlphaSignal.status == "TARGET_HIT").count()
    avg_pnl = db.query(func.avg(AlphaSignal.profit_loss)).filter(AlphaSignal.status != "OPEN").scalar() or 0
    
    return {
        "accuracy_pct": round((wins / total) * 100, 1),
        "total_calls": total,
        "profitable_calls": wins,
        "avg_profit_pct": round(avg_pnl, 2)
    }
