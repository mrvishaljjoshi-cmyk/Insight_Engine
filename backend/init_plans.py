import sys
import os

# Add parent dir to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models.subscription import SubscriptionPlan, PlanType

def init_plans():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        plans = [
            {
                "name": PlanType.FREE,
                "price": 0.0,
                "duration_days": 3650,
                "features": {
                    "Multi-Broker": False,
                    "AI Strategy": True,
                    "Live Charts": True,
                    "Auto-Journal": False
                }
            },
            {
                "name": PlanType.BASIC,
                "price": 499.0,
                "duration_days": 30,
                "features": {
                    "Multi-Broker": True,
                    "AI Strategy": True,
                    "Live Charts": True,
                    "Auto-Journal": False
                }
            },
            {
                "name": PlanType.PRO,
                "price": 999.0,
                "duration_days": 30,
                "features": {
                    "Multi-Broker": True,
                    "AI Strategy": True,
                    "Live Charts": True,
                    "Auto-Journal": True
                }
            },
            {
                "name": PlanType.ULTIMATE,
                "price": 2499.0,
                "duration_days": 90,
                "features": {
                    "Multi-Broker": True,
                    "AI Strategy": True,
                    "Live Charts": True,
                    "Auto-Journal": True,
                    "Priority Support": True
                }
            }
        ]

        for p in plans:
            existing = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == p["name"]).first()
            if not existing:
                plan = SubscriptionPlan(**p)
                db.add(plan)
                print(f"Added plan: {p['name']}")
        
        db.commit()
        print("Subscription plans initialized successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_plans()
