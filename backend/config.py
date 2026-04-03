import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://insight_user:insight_pass@localhost/insight_db")
SECRET_KEY = os.getenv("SECRET_KEY", "BqWcL2tUnbeBUFKyVCa4KwmJA0KIBp8kdoT9S1BPxxA")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "ko_W-vG8ilgGV7TESUWovhFf5W26ausrFLYCL3AUmu0=")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
AI_MODEL = os.getenv("AI_MODEL", "llama3.2:3b")
