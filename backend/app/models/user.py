import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    Admin = "Admin"
    Trader = "Trader"
    Developer = "Developer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Nullable for OAuth-only users
    role = Column(Enum(UserRole), default=UserRole.Trader)
    is_active = Column(Boolean, default=True)
