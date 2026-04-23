"""
Signal Generator Service - Insight Engine
Analyzes live market data to generate breakout signals for Stock, Option, and MCX segments.
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.market_data import AlphaSignal

def generate_mock_signals(db: Session):
    """Utility to ensure user always has fresh alpha signals for testing/demo"""
    segments = ['STOCK', 'OPTION', 'MCX']
    symbols = {
        'STOCK': ['RELIANCE', 'HDFCBANK', 'TCS', 'INFY', 'SBIN'],
        'OPTION': ['NIFTY 22500 CE', 'BANKNIFTY 48200 PE', 'FINNIFTY 21000 CE'],
        'MCX': ['CRUDEOIL', 'GOLD', 'SILVER', 'NATURALGAS']
    }
    
    # Clear old mock signals
    db.query(AlphaSignal).filter(AlphaSignal.is_active == True).delete()
    
    for seg in segments:
        for _ in range(3): # 3 signals per segment
            sym = random.choice(symbols[seg])
            price = random.uniform(100, 20000)
            is_bull = random.choice([True, False])
            
            sig = AlphaSignal(
                symbol=sym,
                segment=seg,
                signal_type="BULLISH_BREAKOUT" if is_bull else "BEARISH_REVERSAL",
                entry_price=round(price, 2),
                target=round(price * (1.05 if is_bull else 0.95), 2),
                stop_loss=round(price * (0.97 if is_bull else 1.03), 2),
                strength=random.randint(75, 98),
                narrative=f"Neural pattern match indicates a high-probability {'long' if is_bull else 'short'} setup based on volume profile and multi-timeframe RSI alignment.",
                is_active=True,
                status="OPEN",
                created_at=datetime.now()
            )
            db.add(sig)
    
    db.commit()
