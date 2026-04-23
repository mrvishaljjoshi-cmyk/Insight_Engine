from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import asyncio
import random
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Simulated market data for NIFTY 50
# In production, this would connect to broker WebSocket feeds


class MarketDataStream:
    """Simulated market data streamer"""

    def __init__(self):
        self.base_price = 22500.0
        self.current_price = self.base_price
        self.ohlc = {
            "open": self.base_price,
            "high": self.base_price,
            "low": self.base_price,
            "close": self.base_price
        }
        self.last_update = datetime.now(timezone.utc)

    def generate_tick(self) -> dict:
        """Generate a simulated market tick"""
        # Random price movement
        change = random.uniform(-15, 15)
        self.current_price += change

        # Update OHLC
        if self.current_price > self.ohlc["high"]:
            self.ohlc["high"] = self.current_price
        if self.current_price < self.ohlc["low"]:
            self.ohlc["low"] = self.current_price
        self.ohlc["close"] = self.current_price

        now = datetime.now(timezone.utc)

        return {
            "symbol": "NIFTY 50",
            "price": round(self.current_price, 2),
            "change": round(change, 2),
            "change_percent": round((change / self.current_price) * 100, 2),
            "timestamp": now.isoformat(),
            "unix_timestamp": now.timestamp(),
            "ohlc": {
                "open": round(self.ohlc["open"], 2),
                "high": round(self.ohlc["high"], 2),
                "low": round(self.ohlc["low"], 2),
                "close": round(self.ohlc["close"], 2)
            }
        }

    def reset_ohlc(self):
        """Reset OHLC for new candle"""
        self.ohlc = {
            "open": self.current_price,
            "high": self.current_price,
            "low": self.current_price,
            "close": self.current_price
        }


# Global market data instance
market_data = MarketDataStream()


@router.websocket("/market-data")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time market data"""
    await websocket.accept()
    client_ip = websocket.client.host if websocket.client else "unknown"
    logger.info(f"WebSocket client connected from {client_ip}")

    try:
        while True:
            # Generate market tick
            data = market_data.generate_tick()

            # Send to client
            await websocket.send_text(json.dumps(data))

            # Wait before next tick (1 second)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from {client_ip}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@router.websocket("/market-data/{symbol}")
async def websocket_symbol_endpoint(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for specific symbol data"""
    await websocket.accept()
    client_ip = websocket.client.host if websocket.client else "unknown"
    logger.info(f"WebSocket client connected for {symbol} from {client_ip}")

    # Validate symbol
    valid_symbols = ["NIFTY 50", "BANKNIFTY", "SENSEX", "FINNIFTY"]
    if symbol.upper() not in [s.upper() for s in valid_symbols]:
        await websocket.send_text(json.dumps({
            "error": f"Invalid symbol. Valid symbols: {valid_symbols}"
        }))
        await websocket.close()
        return

    try:
        while True:
            # Generate symbol-specific market data
            base = {"NIFTY 50": 22500, "BANKNIFTY": 48000, "SENSEX": 74000, "FINNIFTY": 21000}.get(symbol.upper(), 22500)
            change = random.uniform(-20, 20)
            price = base + change

            data = {
                "symbol": symbol.upper(),
                "price": round(price, 2),
                "change": round(change, 2),
                "change_percent": round((change / base) * 100, 2),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        logger.info(f"WebSocket client for {symbol} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
