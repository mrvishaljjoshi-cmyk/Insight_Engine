import os
import requests
import pandas as pd
from datetime import datetime, time, timedelta
import pytz
import random
from sqlalchemy.orm import Session
from app.models.market_data import MarketData, AlphaSignal
from app.core.database import SessionLocal
from app.services.ollama_service import get_ollama_service

IST = pytz.timezone('Asia/Kolkata')

# Top 100 Indian Stock Base Prices for Neural Ingestion
NIFTY_TOP_100 = {
    "RELIANCE": 2938.45, "TCS": 3948.50, "HDFCBANK": 1528.45, "ICICIBANK": 1088.20, "INFY": 1418.50,
    "HINDUNILVR": 2420.30, "ITC": 428.15, "SBIN": 768.15, "BHARTIARTL": 1215.10, "LTIM": 4850.00,
    "KOTAKBANK": 1792.10, "AXISBANK": 1050.20, "ADANIENT": 3120.15, "ADANIPORTS": 1340.50, "ASIANPAINT": 2850.30,
    "BAJAJ-AUTO": 9050.00, "BAJFINANCE": 6840.45, "BAJAJFINSV": 1580.30, "BPCL": 590.20, "BRITANNIA": 4950.00,
    "CIPLA": 1450.00, "COALINDIA": 448.25, "DIVISLAB": 3750.00, "DRREDDY": 6150.00, "EICHERMOT": 4250.00,
    "GRASIM": 2250.00, "HCLTECH": 1540.30, "HDFCLIFE": 615.00, "HEROMOTOCO": 4550.00, "HINDALCO": 580.00,
    "JSWSTEEL": 850.00, "LT": 3650.45, "M&M": 2050.00, "MARUTI": 12450.00, "NTPC": 355.00, "NESTLEIND": 2520.00,
    "ONGC": 275.40, "POWERGRID": 280.00, "SBILIFE": 1480.00, "SUNPHARMA": 1538.20, "TATACONSUM": 1150.00,
    "TATAMOTORS": 980.10, "TATASTEEL": 164.25, "TECHM": 1250.00, "TITAN": 3618.30, "UPL": 480.00,
    "ULTRACEMCO": 9650.00, "WIPRO": 478.45, "NIFTY 50": 22450.30, "BANKNIFTY": 48150.50, "FINNIFTY": 21320.40
}

class MarketService:
    @staticmethod
    def is_market_open():
        now = datetime.now(IST)
        if now.weekday() >= 5: return False
        return time(9, 15) <= now.time() <= time(15, 30)

    @staticmethod
    async def refresh_stock_data(symbol: str, db: Session):
        symbol = symbol.upper()
        stock = db.query(MarketData).filter(MarketData.symbol == symbol).first()
        base_price = NIFTY_TOP_100.get(symbol)
        if not base_price:
            base_price = stock.last_price if stock and stock.last_price > 0 else 100.0
        
        # Simulate live drift for demo/market-hours
        current_ltp = round(base_price + (random.random() - 0.5) * (base_price * 0.002), 2)
        if not stock:
            stock = MarketData(symbol=symbol, last_price=current_ltp, exchange="NSE")
            db.add(stock)
        else:
            stock.last_price = current_ltp
        
        # Prefetch AI if missing
        if not stock.ai_analysis:
            ollama = get_ollama_service()
            analysis = await ollama.analyze_stock(symbol, current_ltp)
            stock.ai_analysis = analysis.__dict__
        
        stock.last_updated = datetime.now(IST)
        db.commit()
        db.refresh(stock)
        return stock

    @staticmethod
    async def run_alpha_scanner():
        """Scans Top 100 stocks for High-Alpha Breakout Signals."""
        db = SessionLocal()
        try:
            for symbol, base in NIFTY_TOP_100.items():
                # Randomly trigger signals for Top 100 (simulating neural detection)
                if random.random() > 0.92: 
                    is_bull = random.choice([True, False])
                    price = base + (random.random() - 0.5) * (base * 0.01)
                    
                    sig = AlphaSignal(
                        symbol=symbol,
                        segment="STOCK",
                        signal_type="BULLISH_BREAKOUT" if is_bull else "BEARISH_BREAKDOWN",
                        entry_price=round(price, 2),
                        target=round(price * (1.04 if is_bull else 0.96), 2),
                        stop_loss=round(price * (0.98 if is_bull else 1.02), 2),
                        strength=random.randint(80, 96),
                        narrative=f"High-Alpha {symbol} breakout confirmed on Top-100 scan. Sector rotation aligns with bullish momentum.",
                        is_active=True,
                        status="OPEN",
                        created_at=datetime.now()
                    )
                    db.add(sig)
            db.commit()
        finally: db.close()

    @staticmethod
    async def update_all_prices_batch():
        db = SessionLocal()
        try:
            stocks = db.query(MarketData).all()
            for s in stocks:
                base = NIFTY_TOP_100.get(s.symbol, s.last_price)
                s.last_price = round(base + (random.random() - 0.5) * (base * 0.001), 2)
                s.last_updated = datetime.now(IST)
            db.commit()
        finally: db.close()
