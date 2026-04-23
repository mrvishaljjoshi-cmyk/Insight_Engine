from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, BrokerCredential
from app.models.market_data import MarketData
from app.services.broker_factory import BrokerFactory
from app.services.ollama_service import get_ollama_service, StockAnalysis, OptionsSuggestion

router = APIRouter()

class AIAnalysisRequest(BaseModel):
    symbol: str
    current_price: float
    avg_price: float = None
    quantity: int = 0

def prune_stock_data(data: List[Any]) -> List[Dict[str, Any]]:
    """
    Simplify holdings/positions data to reduce token usage.
    Returns only 'symbol', 'ltp', and 'pnl'.
    """
    pruned = []
    for item in data:
        # Handle both Pydantic models and dictionaries
        if hasattr(item, 'model_dump'):
            item_dict = item.model_dump()
        elif hasattr(item, 'dict'):
            item_dict = item.dict()
        else:
            item_dict = item
            
        pruned.append({
            "symbol": item_dict.get("tradingsymbol", item_dict.get("symbol", "")),
            "ltp": float(item_dict.get("last_price", item_dict.get("ltp", 0))),
            "pnl": float(item_dict.get("pnl", 0)),
            "average_price": float(item_dict.get("average_price", 0)),
            "quantity": int(item_dict.get("quantity", 0))
        })
    return pruned

@router.get("/summary/holdings")
async def get_holdings_summary(
    fresh: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    """Generate AI summary for all holdings with persistence"""
    # 1. Get all active brokers
    brokers = db.query(BrokerCredential).filter(
        BrokerCredential.user_id == current_user.id,
        BrokerCredential.is_active == True
    ).all()

    if not brokers:
        raise HTTPException(status_code=404, detail="No active broker connections found.")

    all_holdings = []
    for broker in brokers:
        try:
            broker_instance = BrokerFactory.get_broker(broker.broker_name, broker.credentials, user_id=current_user.id)
            holdings_data = broker_instance.get_holdings()
            all_holdings.extend(prune_stock_data(holdings_data))
        except Exception as e:
            print(f"Error fetching holdings for AI: {e}")
            continue

    if not all_holdings:
        return {"summary": "No holdings found to analyze.", "analyses": []}

    ollama = get_ollama_service()
    final_analyses = []

    for holding in all_holdings:
        symbol = holding['symbol'].upper()
        # 2. Check if we have fresh analysis in market_data
        stock_record = db.query(MarketData).filter(MarketData.symbol == symbol).first()
        
        if not fresh and stock_record and stock_record.ai_analysis and "market_narrative" in stock_record.ai_analysis:
            # Use cached only if it contains the new market_narrative field
            final_analyses.append(stock_record.ai_analysis)
        else:
            # Generate new and save
            analysis = await ollama.analyze_stock(
                symbol=symbol,
                current_price=holding['ltp'],
                avg_price=holding['average_price'],
                quantity=holding['quantity'],
                pnl=holding['pnl']
            )
            analysis_dict = analysis.__dict__
            final_analyses.append(analysis_dict)
            
            # Save to global market_data for future reference by ANY user
            if stock_record:
                stock_record.ai_analysis = analysis_dict
                db.add(stock_record)
            else:
                # Create record if missing (unlikely after full sync but safe)
                new_stock = MarketData(symbol=symbol, ai_analysis=analysis_dict, last_price=holding['ltp'])
                db.add(new_stock)
    
    db.commit()

    return {
        "summary": f"Analyzed {len(final_analyses)} holdings. Strategy updated.",
        "analyses": final_analyses
    }

from app.services.market_service import MarketService

@router.get("/analyze/{symbol}")
async def get_single_stock_analysis(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI analysis for a specific stock"""
    symbol = symbol.upper()
    brokers = db.query(BrokerCredential).filter(
        BrokerCredential.user_id == current_user.id,
        BrokerCredential.is_active == True
    ).all()

    found_holding = None
    for b in brokers:
        try:
            broker_instance = BrokerFactory.get_broker(b.broker_name, b.credentials, user_id=current_user.id)
            holdings = broker_instance.get_holdings()
            for h in holdings:
                h_dict = h.model_dump() if hasattr(h, 'model_dump') else h
                if h_dict.get('tradingsymbol') == symbol or h_dict.get('symbol') == symbol:
                    found_holding = h_dict
                    break
            if found_holding: break
        except: continue

    if found_holding:
        ollama = get_ollama_service()
        analysis = await ollama.analyze_stock(
            symbol=symbol,
            current_price=float(found_holding.get('last_price', found_holding.get('ltp', 0))),
            avg_price=float(found_holding.get('average_price', found_holding.get('avg_price', 0))),
            quantity=int(found_holding.get('quantity', 0)),
            pnl=float(found_holding.get('pnl', 0))
        )
        return analysis.__dict__
    
    # Fallback: Analyze stock even if not in holdings by fetching from MarketService
    stock = await MarketService.refresh_stock_data(symbol, db)
    if stock:
        return stock.ai_analysis
        
    raise HTTPException(status_code=404, detail="Symbol not found in holdings or market data.")

@router.get("/options/suggestions/{index}")
async def get_options_suggestions(
    index: str,
    spot_price: float = 22450.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI suggestions for Call/Put options"""
    if index.upper() not in ["NIFTY", "BANKNIFTY", "FINNIFTY"]:
        raise HTTPException(status_code=400, detail="Invalid index")
        
    ollama = get_ollama_service()
    # Mock option chain
    mock_option_chain = []
    strikes = [round(spot_price / 50) * 50 + i * 50 for i in range(-5, 6)]
    for strike in strikes:
        mock_option_chain.append({
            "strike_price": strike,
            "option_type": "CE",
            "last_price": max(10, 200 - abs(strike - spot_price) * 0.5),
            "open_interest": 1000000
        })
        mock_option_chain.append({
            "strike_price": strike,
            "option_type": "PE",
            "last_price": max(10, 200 - abs(strike - spot_price) * 0.5),
            "open_interest": 1000000
        })
        
    suggestions = await ollama.suggest_options(index.upper(), spot_price, mock_option_chain)
    return [s.__dict__ for s in suggestions]
