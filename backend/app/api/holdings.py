"""
Holdings API - Fetch and manage holdings across all linked broker accounts.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Union
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, BrokerCredential
from app.services.broker_factory import BrokerFactory

router = APIRouter()

# Global thread pool for I/O bound broker calls
executor = ThreadPoolExecutor(max_workers=10)

class HoldingItem(BaseModel):
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    total_value: float
    profit_loss: float
    profit_loss_percent: float
    exchange: str
    product_type: str
    broker_name: str


class HoldingsResponse(BaseModel):
    total_invested: float
    total_current_value: float
    total_profit_loss: float
    total_profit_loss_percent: float
    holdings: List[Dict[str, Any]]
    by_broker: Dict[str, Union[List[Dict[str, Any]], Dict[str, Any]]]

async def fetch_broker_holdings(broker, user_id):
    """Worker function to fetch holdings from a single broker in a thread."""
    loop = asyncio.get_event_loop()
    try:
        broker_instance = BrokerFactory.get_broker(
            broker.broker_name,
            broker.credentials,
            user_id=user_id
        )
        # Wrap blocking SDK call in thread
        holdings_data = await loop.run_in_executor(executor, broker_instance.get_holdings)
        return broker.broker_name, holdings_data
    except Exception as e:
        return broker.broker_name, {"error": str(e)}

@router.get("/", response_model=HoldingsResponse)
async def get_all_holdings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get holdings across all active broker connections in parallel for the authenticated user"""
    brokers = db.query(BrokerCredential).filter(
        BrokerCredential.user_id == current_user.id,
        BrokerCredential.is_active == True
    ).all()

    if not brokers:
        return {
            'total_invested': 0,
            'total_current_value': 0,
            'total_profit_loss': 0,
            'total_profit_loss_percent': 0,
            'holdings': [],
            'by_broker': {}
        }

    # Parallel Execution Protocol
    tasks = [fetch_broker_holdings(b, current_user.id) for b in brokers]
    results = await asyncio.gather(*tasks)

    all_holdings = []
    by_broker = {}
    total_invested = 0.0
    total_current_value = 0.0

    for broker_name, holdings_data in results:
        if isinstance(holdings_data, dict) and "error" in holdings_data:
            by_broker[broker_name] = holdings_data
            continue

        broker_holdings = []
        for h in holdings_data:
            if hasattr(h, 'model_dump'):
                h_dict = h.model_dump()
            else:
                h_dict = h
            
            qty = float(h_dict.get('quantity', 0))
            avg = float(h_dict.get('average_price', 0))
            ltp = float(h_dict.get('last_price', 0))
            pnl = float(h_dict.get('pnl', 0))

            invested = qty * avg
            current_val = qty * ltp
            
            if invested == 0 and pnl != 0:
                invested = current_val - pnl
            
            holding_item = {
                'symbol': h_dict.get('tradingsymbol', 'Unknown'),
                'quantity': int(qty),
                'avg_price': round(avg, 2),
                'current_price': round(ltp, 2),
                'total_value': round(current_val, 2),
                'profit_loss': round(pnl, 2),
                'profit_loss_percent': round((pnl / invested * 100) if invested > 0 else 0, 2),
                'exchange': h_dict.get('exchange', 'NSE'),
                'product_type': h_dict.get('product', 'CNC'),
                'broker_name': broker_name
            }
            broker_holdings.append(holding_item)
            total_invested += invested
            total_current_value += current_val

        by_broker[broker_name] = broker_holdings
        all_holdings.extend(broker_holdings)

    total_profit_loss = total_current_value - total_invested
    total_profit_loss_percent = ((total_current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0

    return {
        'total_invested': round(total_invested, 2),
        'total_current_value': round(total_current_value, 2),
        'total_profit_loss': round(total_profit_loss, 2),
        'total_profit_loss_percent': round(total_profit_loss_percent, 2),
        'holdings': all_holdings,
        'by_broker': by_broker
    }


@router.get("/{broker_id}")
def get_broker_holdings(
    broker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get holdings from a specific broker"""
    broker = db.query(BrokerCredential).filter(
        BrokerCredential.id == broker_id,
        BrokerCredential.user_id == current_user.id
    ).first()

    if not broker:
        raise HTTPException(
            status_code=404,
            detail="Broker connection not found"
        )

    try:
        broker_instance = BrokerFactory.get_broker(
            broker.broker_name,
            broker.credentials,
            user_id=current_user.id
        )
        # Returns List[HoldingSchema]
        return broker_instance.get_holdings()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch holdings: {str(e)}"
        )
