import pyotp
from SmartApi import SmartConnect
from brokers.base import BaseBrokerProvider
from typing import List, Dict, Any

class AngelOneProvider(BaseBrokerProvider):
    def __init__(self, api_key: str, client_code: str, pin: str, totp_secret: str, api_secret: str = None):
        self.api_key = api_key
        self.client_code = client_code
        self.pin = pin
        self.totp_secret = totp_secret
        self.api_secret = api_secret
        self.smart_api = SmartConnect(api_key=self.api_key)
        self.access_token = None

    def authenticate(self) -> str:
        totp = pyotp.TOTP(self.totp_secret).now()
        # SmartAPI login uses API Secret as Private Key
        data = self.smart_api.generateSession(self.client_code, self.pin, totp)
        if data['status']:
            self.access_token = data['data']['jwtToken']
            return self.access_token
        raise Exception(f"Angel One Auth Failed: {data.get('message')}")

    def fetch_holdings(self) -> List[Dict[str, Any]]:
        holdings_resp = self.smart_api.holding()
        if holdings_resp['status']:
            return holdings_resp['data']
        raise Exception(f"Failed to fetch holdings: {holdings_resp.get('message')}")

    def fetch_trades(self) -> List[Dict[str, Any]]:
        trades_resp = self.smart_api.orderBook()
        if trades_resp['status']:
            return trades_resp['data']
        raise Exception(f"Failed to fetch trades: {trades_resp.get('message')}")

    def place_robo_order(self, symbol: str, qty: int, target: float, sl: float) -> str:
        # Placeholder for real order placement via SmartAPI
        return f"ROBO_{symbol}_DEPOLYED"

    def get_ltp(self, symbol: str) -> float:
        return 0.0 
