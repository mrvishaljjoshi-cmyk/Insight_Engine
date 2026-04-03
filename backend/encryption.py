from cryptography.fernet import Fernet
import config

_fernet = Fernet(config.ENCRYPTION_KEY.encode())

def encrypt(data: str) -> str:
    if not data:
        return data
    return _fernet.encrypt(data.encode()).decode()

def decrypt(data: str) -> str:
    if not data:
        return data
    try:
        return _fernet.decrypt(data.encode()).decode()
    except Exception:
        return data # Fallback if already decrypted or wrong key
