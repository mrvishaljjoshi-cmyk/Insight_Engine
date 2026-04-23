import asyncio
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.signal_generator import generate_mock_signals

logger = logging.getLogger(__name__)

from app.services.market_service import MarketService

async def signal_worker_loop():
    """Background task to ensure fresh AI alpha signals are always available."""
    logger.info("SIGNAL_WORKER: Initializing Neural Discovery...")
    while True:
        try:
            # 1. Run Top-100 Scanner
            await MarketService.run_alpha_scanner()
            # 2. Update all prices in DB
            await MarketService.update_all_prices_batch()
            
            db = SessionLocal()
            try:
                # 3. Handle specific signal cleanup/mocking if needed
                generate_mock_signals(db)
                logger.info("SIGNAL_WORKER: Top-100 scan complete. Neural matrix synchronized.")
            finally:
                db.close()
            # Refresh every 2 minutes for high frequency
            await asyncio.sleep(120)
        except Exception as e:
            logger.error(f"SIGNAL_WORKER_ERROR: {e}")
            await asyncio.sleep(30)
