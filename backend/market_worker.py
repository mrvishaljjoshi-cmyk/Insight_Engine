import asyncio
import time
from app.services.market_service import MarketService
from app.core.database import engine, Base

async def main():
    print("🚀 Advanced Market Data Worker Starting...")
    
    # 1. Initial Symbol Registry Sync
    MarketService.sync_nse_symbols()
    
    count = 0
    while True:
        try:
            # 2. High-frequency price updates (Every 5 seconds during market hours)
            if MarketService.is_market_open():
                await MarketService.update_all_prices_batch()
                # Run Scanner for breakouts
                await MarketService.run_alpha_scanner()
                # Check results of past signals
                await MarketService.check_signal_performance()
            
            # 3. Low-frequency background AI (Every 30 seconds)
            if count % 6 == 0:
                await MarketService.background_ai_queue()
                
            count += 1
        except Exception as e:
            print(f"Worker Loop Error: {e}")
            
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
