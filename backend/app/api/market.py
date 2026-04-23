from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.market_data import MarketData
from app.services.market_service import MarketService
from app.services.ollama_service import get_ollama_service

router = APIRouter()

@router.get("/search")
def search_symbols(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search for valid NSE symbols"""
    if not q or len(q) < 2:
        return []
    
    results = db.query(MarketData).filter(
        MarketData.symbol.ilike(f"%{q}%") | 
        MarketData.company_name.ilike(f"%{q}%")
    ).limit(10).all()
    
    return [
        {
            "symbol": r.symbol,
            "name": r.company_name,
            "ltp": r.last_price,
            "exchange": r.exchange
        } for r in results
    ]

@router.get("/quote/{symbol}")
async def get_quote(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get live price and AI summary (Triggers Auto-Refresh)"""
    # Force refresh data from MarketService
    stock = await MarketService.refresh_stock_data(symbol, db)
    
    if not stock:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found.")

    return {
        "symbol": stock.symbol,
        "name": stock.company_name,
        "ltp": stock.last_price,
        "ai_analysis": stock.ai_analysis,
        "last_updated": stock.last_updated
    }

@router.post("/sync-init")
def trigger_sync(current_user: User = Depends(get_current_user)):
    """Admin only: Trigger initial NSE sync"""
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    MarketService.sync_nse_symbols()
    return {"message": "Sync started in background"}
