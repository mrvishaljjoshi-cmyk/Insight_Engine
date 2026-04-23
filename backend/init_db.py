import os
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
# Import all models here
import app.models as models
from app.models.user import User, UserRole

# Delete old DB if exists to apply new schema (Dev only)
if os.path.exists("./insight.db"):
    os.remove("./insight.db")

# Create tables
Base.metadata.create_all(bind=engine)

def init():
    db = SessionLocal()
    # Create admin user
    admin = User(
        username="vjadmin",
        email="admin@vjprojects.co.in",
        mobile_no="9999999999",
        hashed_password=get_password_hash("123456"),
        role=UserRole.Admin,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.close()
    print("Database initialized with admin: vjadmin")

if __name__ == "__main__":
    init()
