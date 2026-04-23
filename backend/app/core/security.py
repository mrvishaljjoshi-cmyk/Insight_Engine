from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Initialize Fernet for credential encryption
_fernet = None

def get_encryption_key() -> bytes:
    """Derive a robust 32-byte key from the ENCRYPTION_KEY using PBKDF2"""
    # Use a fixed salt for consistency across restarts, or a configured salt
    salt = b"insight_engine_salt_v1" 
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(settings.ENCRYPTION_KEY.encode()))

if settings.ENCRYPTION_KEY:
    try:
        _fernet = Fernet(get_encryption_key())
    except Exception as e:
        if settings.ENV == "production":
            raise RuntimeError(f"ENCRYPTION_KEY is invalid for production: {e}")
elif settings.ENV == "production":
    raise RuntimeError("ENCRYPTION_KEY must be set in production environment")


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


from app.core.redis import redis_client

def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and check if blacklisted"""
    try:
        # Check blacklist first
        if redis_client.get(f"bl_{token}"):
            return None
            
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def encrypt_credentials(credentials: dict) -> str:
    """Encrypt broker credentials using derived key"""
    json_str = json.dumps(credentials)
    if _fernet:
        return _fernet.encrypt(json_str.encode()).decode()
    
    if settings.ENV == "production":
        raise RuntimeError("Encryption failed: Fernet not initialized")
        
    return base64.b64encode(json_str.encode()).decode()


def get_old_encryption_key() -> bytes:
    """Old weak key derivation for backward compatibility"""
    key_bytes = settings.ENCRYPTION_KEY.encode()
    if len(key_bytes) < 32:
        key_bytes = key_bytes.ljust(32, b'0')
    elif len(key_bytes) > 32:
        key_bytes = key_bytes[:32]
    return base64.urlsafe_b64encode(key_bytes)

_old_fernet = None
try:
    if settings.ENCRYPTION_KEY:
        _old_fernet = Fernet(get_old_encryption_key())
except Exception:
    pass

def decrypt_credentials(encrypted: str) -> dict:
    """Decrypt broker credentials with fallback support"""
    # 1. Try new PBKDF2 method
    if _fernet:
        try:
            decrypted = _fernet.decrypt(encrypted.encode())
            return json.loads(decrypted)
        except Exception:
            pass

    # 2. Try old padded method (fallback)
    if _old_fernet:
        try:
            decrypted = _old_fernet.decrypt(encrypted.encode())
            return json.loads(decrypted)
        except Exception:
            pass
    
    # 3. Dev fallback (plain base64)
    if settings.ENV != "production":
        try:
            return json.loads(base64.b64decode(encrypted.encode()))
        except:
            pass
            
    return {}


def mask_credentials(credentials: dict) -> dict:
    """Mask sensitive credential values for display"""
    masked = {}
    for key, value in credentials.items():
        if isinstance(value, str) and len(value) > 4:
            masked[key] = value[:2] + "***" + value[-2:]
        else:
            masked[key] = "***"
    return masked


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user object from JWT token"""
    token = credentials.credentials
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
        
    return user
