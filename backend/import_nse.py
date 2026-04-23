import pandas as pd
import sys
import os

# Add parent dir to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.models.market_data import MarketData

def manual_import():
    csv_path = "/tmp/nse_list.csv"
    if not os.path.exists(csv_path):
        print("CSV not found!")
        return

    db = SessionLocal()
    try:
        df = pd.read_csv(csv_path)
        # Strip whitespace from columns
        df.columns = df.columns.str.strip()
        
        print(f"Starting import of {len(df)} symbols...")
        count = 0
        for _, row in df.iterrows():
            symbol = str(row['SYMBOL']).strip()
            name = str(row['NAME OF COMPANY']).strip()
            
            existing = db.query(MarketData).filter(MarketData.symbol == symbol).first()
            if not existing:
                new_stock = MarketData(
                    symbol=symbol,
                    company_name=name,
                    last_price=0.0
                )
                db.add(new_stock)
                count += 1
                if count % 100 == 0:
                    db.commit()
                    print(f"Imported {count}...")
        
        db.commit()
        print(f"Done! Imported {count} new symbols.")
    except Exception as e:
        print(f"Import error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    manual_import()
