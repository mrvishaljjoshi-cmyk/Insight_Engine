from fastapi import FastAPI, Depends, HTTPException, status, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import json
import redis
import logging

import models, database, auth, ai_service, notification_service, config, encryption
from brokers.angelone import AngelOneProvider

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Insight_Engine")

try:
    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0, decode_responses=True)
    r.ping()
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    r = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Unauthorized")
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise credentials_exception
    except auth.jwt.JWTError: raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None: raise credentials_exception
    return user

def run_deep_research(user_id: int, symbol: str):
    db = next(database.get_db())
    try:
        if r: r.setex(f"processing:{symbol}:{user_id}", 600, "true")
        research = ai_service.AIService.chat(f"RESEARCH: {symbol}")
        if r:
            r.delete(f"processing:{symbol}:{user_id}")
            r.setex(f"analysis:{symbol}", 3600, json.dumps({"symbol": symbol, "analysis": research, "timestamp": datetime.utcnow().isoformat()}))
        latest = db.query(models.PortfolioSnapshot).filter(models.PortfolioSnapshot.user_id == user_id).order_by(models.PortfolioSnapshot.timestamp.desc()).first()
        if latest:
            data = latest.data
            for h in data:
                if h['tradingsymbol'] == symbol: h['ai_analysis'] = research
            latest.data = data; db.commit()
    except Exception as e:
        logger.error(f"Error in deep research for {symbol}: {e}")
        if r: r.delete(f"processing:{symbol}:{user_id}")

@app.post("/register")
def register(payload: dict = Body(...), db: Session = Depends(database.get_db)):
    email = payload.get("email"); password = payload.get("password")
    if db.query(models.User).filter(models.User.email == email).first(): raise HTTPException(status_code=400, detail="User already exists")
    new_user = models.User(email=email, hashed_password=auth.get_password_hash(password))
    db.add(new_user); db.commit(); db.refresh(new_user); return {"user_id": new_user.id}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/subscription/status")
def get_subscription(current_user: models.User = Depends(get_current_user)):
    return {
        "has_broker": len(current_user.brokers) > 0,
        "email": current_user.email,
        "telegram_id": current_user.telegram_id,
        "is_telegram_verified": current_user.is_telegram_verified,
        "is_email_verified": current_user.is_email_verified,
        "current_plan": "Pro Alpha" if current_user.is_subscribed else "Free Trial"
    }

@app.post("/profile/verify")
def verify_notifications(data: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    current_user.email = data.get('email', current_user.email)
    current_user.telegram_id = data.get('telegram_id', current_user.telegram_id)
    current_user.is_email_verified = True; current_user.is_telegram_verified = True
    db.commit(); notification_service.NotificationService.send_welcome(current_user.email, current_user.telegram_id)
    return {"message": "Profile verified and notifications enabled"}

@app.post("/test/angelone")
def test_angelone(data: dict):
    provider = AngelOneProvider(data['api_key'], data['client_code'], data['pin'], data['totp_secret'], data.get('api_secret'))
    try:
        provider.authenticate(); return {"message": "Valid Credentials"}
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))

@app.post("/connect/angelone")
def connect_angelone(data: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    # Encrypt sensitive data
    enc_api_key = encryption.encrypt(data['api_key'])
    enc_totp_secret = encryption.encrypt(data['totp_secret'])
    enc_pin = encryption.encrypt(data['pin'])
    enc_api_secret = encryption.encrypt(data.get('api_secret')) if data.get('api_secret') else None

    provider = AngelOneProvider(data['api_key'], data['client_code'], data['pin'], data['totp_secret'], data.get('api_secret'))
    try:
        provider.authenticate()
        existing = db.query(models.Broker).filter(models.Broker.user_id == current_user.id).first()
        if existing:
            existing.client_code = data['client_code']
            existing.api_key = enc_api_key
            existing.totp_secret = enc_totp_secret
            existing.pin = enc_pin
            existing.api_secret = enc_api_secret
        else:
            db.add(models.Broker(
                provider="angelone", 
                client_code=data['client_code'], 
                api_key=enc_api_key, 
                totp_secret=enc_totp_secret, 
                pin=enc_pin, 
                api_secret=enc_api_secret, 
                user_id=current_user.id
            ))
        db.commit(); return {"message": "Broker linked successfully"}
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))

@app.get("/portfolio/summarize")
def summarize_portfolio(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    if not current_user.brokers: return {"connected": False}
    if r:
        cached = r.get(f"portfolio:{current_user.id}")
        if cached: return json.loads(cached)
    return {"connected": True, "sync_required": True}

@app.post("/portfolio/sync")
def sync_portfolio(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    if not current_user.brokers: raise HTTPException(status_code=400, detail="No broker connected")
    broker = current_user.brokers[0]
    
    # Decrypt sensitive data
    api_key = encryption.decrypt(broker.api_key)
    totp_secret = encryption.decrypt(broker.totp_secret)
    pin = encryption.decrypt(broker.pin)
    api_secret = encryption.decrypt(broker.api_secret) if broker.api_secret else None

    provider = AngelOneProvider(api_key, broker.client_code, pin, totp_secret, api_secret)
    try:
        provider.authenticate(); holdings = provider.fetch_holdings()
        formatted = []
        for h in holdings:
            avg = float(h.get("averageprice", 0)); qty = int(h.get("quantity", 0)); ltp = float(h.get("ltp", 0))
            invested = round(qty * avg, 2); current_val = round(qty * ltp, 2); pnl = round(current_val - invested, 2)
            formatted.append({
                "tradingsymbol": h.get("tradingsymbol"), "exchange": h.get("exchange", "NSE"), "quantity": qty, "averageprice": avg, "ltp": ltp,
                "pnl": pnl, "pnlpercentage": round((pnl/invested*100),2) if invested>0 else 0, "invested": invested, "current_value": current_val
            })
        total = sum(h['current_value'] for h in formatted); invested_total = sum(h['invested'] for h in formatted)
        for h in formatted: h['target'] = round(h['ltp'] * 1.1, 2); h['sl'] = round(h['ltp'] * 0.95, 2)
        summary = ai_service.AIService.summarize_portfolio(formatted)
        db.add(models.PortfolioSnapshot(user_id=current_user.id, data=formatted, total_value=total, ai_summary=summary))
        db.commit(); result = {"summary": summary, "holdings": formatted, "total_value": total, "invested_value": invested_total, "connected": True}
        if r: r.setex(f"portfolio:{current_user.id}", 300, json.dumps(result))
        return result
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))

@app.post("/portfolio/analyze-share")
def analyze_share(symbol: str, background_tasks: BackgroundTasks, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    if r and r.get(f"processing:{symbol}:{current_user.id}"): return {"message": "Analysis in progress...", "processing": True}
    background_tasks.add_task(run_deep_research, current_user.id, symbol)
    return {"message": "Analysis initialized", "processing": True}

@app.get("/portfolio/history")
def get_portfolio_history(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    return db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).order_by(models.Transaction.timestamp.desc()).all()

@app.post("/trade/robo")
def place_robo_order(symbol: str, qty: int, target: float, sl: float, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    if not current_user.brokers: raise HTTPException(status_code=400, detail="No broker connected")
    broker = current_user.brokers[0]; val = qty * target; tax = round(val * 0.0015, 2)
    
    # Decrypt sensitive data
    api_key = encryption.decrypt(broker.api_key)
    totp_secret = encryption.decrypt(broker.totp_secret)
    pin = encryption.decrypt(broker.pin)
    api_secret = encryption.decrypt(broker.api_secret) if broker.api_secret else None

    provider = AngelOneProvider(api_key, broker.client_code, pin, totp_secret, api_secret)
    try:
        provider.authenticate(); order_id = provider.place_robo_order(symbol, qty, target, sl)
        db.add(models.Transaction(user_id=current_user.id, broker_id=broker.id, symbol=symbol, transaction_type="SELL_ROBO", quantity=qty, price=target, order_id=order_id))
        db.commit(); return {"message": "Robo order placed", "breakup": {"gross": val, "tax": tax, "net": val - tax}}
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))
