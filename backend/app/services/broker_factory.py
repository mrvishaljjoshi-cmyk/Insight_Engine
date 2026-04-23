"""
Broker Factory - Unified interface for Indian broker integrations.

This module provides a standardized interface for connecting to multiple Indian
broker APIs. Each broker has its own SDK and authentication method, but this
factory abstracts them into a common interface.

Supported Brokers:
    - Zerodha (Kite Connect)
    - Angel One (SmartAPI)
    - Groww (GrowwAPI)
    - Dhan (DhanHQ)
    - Upstox (Upstox Client)
"""
from typing import Dict, Any, Optional, List
import pyotp
from SmartApi import SmartConnect
from kiteconnect import KiteConnect
from growwapi import GrowwAPI
from dhanhq import dhanhq
import upstox_client
from pydantic import BaseModel
from app.core.security import decrypt_credentials
from app.core.cache import cache_response

class BrokerAPIError(Exception):
    """Custom exception for broker API errors."""
    def __init__(self, message: str, broker: str):
        self.message = message
        self.broker = broker
        super().__init__(f"[{broker}] {message}")

class HoldingSchema(BaseModel):
    tradingsymbol: Optional[str] = ""
    exchange: Optional[str] = "NSE"
    isin: Optional[str] = ""
    quantity: Optional[int] = 0
    average_price: Optional[float] = 0.0
    last_price: Optional[float] = 0.0
    pnl: Optional[float] = 0.0
    product: Optional[str] = "CNC"
    realised_quantity: Optional[int] = 0
    t1_quantity: Optional[int] = 0

class PositionSchema(BaseModel):
    tradingsymbol: Optional[str] = ""
    exchange: Optional[str] = "NSE"
    product: Optional[str] = "MIS"
    quantity: Optional[int] = 0
    average_price: Optional[float] = 0.0
    last_price: Optional[float] = 0.0
    pnl: Optional[float] = 0.0
    realised: Optional[float] = 0.0
    unrealised: Optional[float] = 0.0
    buy_quantity: Optional[int] = 0
    sell_quantity: Optional[int] = 0

class BrokerInterface:
    def get_profile(self) -> Dict[str, Any]:
        raise NotImplementedError
    def get_balance(self) -> Dict[str, Any]:
        raise NotImplementedError
    def get_positions(self) -> List[PositionSchema]:
        raise NotImplementedError
    def get_holdings(self) -> List[HoldingSchema]:
        raise NotImplementedError
    def get_trades(self) -> List[Dict[str, Any]]:
        raise NotImplementedError
    def place_order(self, symbol: str, quantity: int, side: str, order_type: str, price: Optional[float] = None) -> Dict[str, Any]:
        raise NotImplementedError

class ZerodhaBroker(BrokerInterface):
    def __init__(self, credentials: Dict[str, Any], user_id: Any = None):
        try:
            self.user_id = user_id
            self.api_key = credentials.get("API Key")
            self.access_token = credentials.get("Access Token")
            self.kite = KiteConnect(api_key=self.api_key)
            if self.access_token:
                self.kite.set_access_token(self.access_token)
        except Exception as e:
            raise BrokerAPIError(f"Initialization failed: {str(e)}", "Zerodha")

    def get_profile(self) -> Dict[str, Any]:
        try:
            return self.kite.profile()
        except Exception as e:
            raise BrokerAPIError(str(e), "Zerodha")

    def get_balance(self) -> Dict[str, Any]:
        try:
            margins = self.kite.margins()
            # Standardize Zerodha response
            equity = margins.get('equity', {})
            return {
                "availablecash": equity.get('available', {}).get('cash', 0),
                "net": equity.get('net', 0),
                "utilised": equity.get('utilised', {}).get('debits', 0)
            }
        except Exception as e:
            raise BrokerAPIError(str(e), "Zerodha")

    @cache_response(ttl=60)
    def get_positions(self) -> List[PositionSchema]:
        try:
            positions = self.kite.positions().get("net", [])
            return [PositionSchema(**p) for p in positions]
        except Exception as e:
            raise BrokerAPIError(str(e), "Zerodha")
        
    @cache_response(ttl=60)
    def get_holdings(self) -> List[HoldingSchema]:
        try:
            holdings = self.kite.holdings()
            return [HoldingSchema(**h) for h in holdings]
        except Exception as e:
            raise BrokerAPIError(str(e), "Zerodha")

    def get_trades(self) -> List[Dict[str, Any]]:
        try:
            return self.kite.trades()
        except Exception as e:
            raise BrokerAPIError(str(e), "Zerodha")

    def place_order(
        self,
        symbol: str,
        quantity: int,
        side: str,
        order_type: str,
        price: Optional[float] = None,
        product: str = "MIS",
        validity: str = "DAY"
    ) -> Dict[str, Any]:
        try:
            order_params = {
                "variety": "regular",
                "tradingsymbol": symbol,
                "exchange": "NFO" if any(x in symbol for x in ["FUT", "OPT"]) else "NSE",
                "transaction_type": side.lower(),
                "quantity": quantity,
                "product": product,
                "order_type": order_type.lower(),
                "validity": validity.lower(),
            }
            if price is not None:
                order_params["price"] = price
                
            order_id = self.kite.place_order(**order_params)
            return {"order_id": order_id, "status": "placed", "broker": "Zerodha"}
        except Exception as e:
            raise BrokerAPIError(str(e), "Zerodha")

class AngelOneBroker(BrokerInterface):
    def __init__(self, credentials: Dict[str, Any], user_id: Any = None):
        self.user_id = user_id
        self.api_key = credentials.get("SmartAPI Key")
        self.client_code = credentials.get("Client ID")
        self.password = credentials.get("Password")
        self.totp_secret = credentials.get("TOTP Secret")
        self.smart_api = SmartConnect(api_key=self.api_key)
        self.session = None

    def login(self):
        try:
            if not self.totp_secret:
                raise BrokerAPIError("TOTP Secret is missing from credentials", "Angel One")
            
            totp = pyotp.TOTP(self.totp_secret).now()
            data = self.smart_api.generateSession(self.client_code, self.password, totp)
            
            if not data:
                raise BrokerAPIError("Received empty response from SmartAPI", "Angel One")
                
            if data.get('status'):
                self.session = data['data']
                return True
            raise BrokerAPIError(data.get('message', 'Login failed'), "Angel One")
        except Exception as e:
            if isinstance(e, BrokerAPIError): raise e
            raise BrokerAPIError(f"Login failed: {str(e)}", "Angel One")

    def get_profile(self) -> Dict[str, Any]:
        try:
            if not self.session: self.login()
            response = self.smart_api.getProfile(self.session['refreshToken'])
            if not response.get('status'):
                raise BrokerAPIError(response.get('message', 'Failed to get profile'), "Angel One")
            return response.get('data', {})
        except Exception as e:
            if isinstance(e, BrokerAPIError): raise e
            raise BrokerAPIError(str(e), "Angel One")

    def get_balance(self) -> Dict[str, Any]:
        try:
            if not self.session: self.login()
            response = self.smart_api.rmsLimit()
            print(f"DEBUG: Angel One raw balance response: {response}")
            if not response or not response.get('status'):
                raise BrokerAPIError(response.get('message', 'Failed to get balance'), "Angel One")
            
            data = response.get('data', {})
            # Ensure we return a flat dict with common field names
            return {
                "availablecash": data.get('availablecash', 0),
                "net": data.get('net', 0),
                "utilised": data.get('utilizedmargin', 0)
            }
        except Exception as e:
            if isinstance(e, BrokerAPIError): raise e
            raise BrokerAPIError(str(e), "Angel One")

    @cache_response(ttl=60)
    def get_positions(self) -> List[PositionSchema]:
        try:
            if not self.session: self.login()
            response = self.smart_api.position()
            if not response.get('status'):
                raise BrokerAPIError(response.get('message', 'Failed to get positions'), "Angel One")
            return [
                PositionSchema(
                    tradingsymbol=p.get('tradingsymbol'),
                    exchange=p.get('exchange'),
                    product=p.get('producttype'),
                    quantity=int(p.get('netqty', 0)),
                    average_price=float(p.get('avgprice', 0)),
                    last_price=float(p.get('ltp', 0)),
                    pnl=float(p.get('pnl', 0)),
                    realised=float(p.get('realisedpnl', 0)),
                    unrealised=float(p.get('unrealisedpnl', 0)),
                    buy_quantity=int(p.get('buyqty', 0)),
                    sell_quantity=int(p.get('sellqty', 0))
                ) for p in response.get('data', [])
            ]
        except Exception as e:
            if isinstance(e, BrokerAPIError): raise e
            raise BrokerAPIError(str(e), "Angel One")
        
    @cache_response(ttl=60)
    def get_holdings(self) -> List[HoldingSchema]:
        try:
            if not self.session: self.login()
            response = self.smart_api.holding()
            if not response or not response.get('status'):
                return []
            
            data = response.get('data')
            if data is None:
                return []
                
            return [
                HoldingSchema(
                    tradingsymbol=h.get('tradingsymbol') or h.get('symbol', ''),
                    exchange=h.get('exchange', 'NSE'),
                    isin=h.get('isin', ''),
                    quantity=int(h.get('quantity', 0)),
                    average_price=float(h.get('avgprice') or h.get('averageprice', 0)),
                    last_price=float(h.get('ltp') or h.get('lastprice', 0)),
                    pnl=float(h.get('pnl', 0)),
                    product=h.get('producttype', 'CNC'),
                    realised_quantity=int(h.get('realisedquantity', 0)),
                    t1_quantity=int(h.get('t1quantity', 0))
                ) for h in data
            ]
        except Exception as e:
            if isinstance(e, BrokerAPIError): raise e
            raise BrokerAPIError(str(e), "Angel One")

    def get_trades(self) -> List[Dict[str, Any]]:
        try:
            if not self.session: self.login()
            response = self.smart_api.tradeBook()
            if not response or not response.get('status'):
                # Return empty list instead of raising if no trades
                return []
            return response.get('data') or []
        except Exception as e:
            # For logging only
            print(f"Angel One Trade Fetch Error: {e}")
            return []

    def place_order(
        self,
        symbol: str,
        quantity: int,
        side: str,
        order_type: str,
        price: Optional[float] = None,
        product: str = "MIS",
        validity: str = "DAY"
    ) -> Dict[str, Any]:
        try:
            if not self.session: self.login()
            order_params = {
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": symbol,
                "exchange": "NFO" if any(x in symbol for x in ["FUT", "OPT"]) else "NSE",
                "transactiontype": side,
                "quantity": str(quantity),
                "producttype": product,
                "ordertype": order_type,
                "validity": validity,
            }
            if price is not None:
                order_params["price"] = str(price)
            response = self.smart_api.placeOrder(order_params)
            if not response.get('status'):
                raise BrokerAPIError(response.get('message', 'Order placement failed'), "Angel One")
            return {
                "order_id": response.get("data", {}).get("orderid"),
                "status": "placed",
                "broker": "Angel One"
            }
        except Exception as e:
            if isinstance(e, BrokerAPIError): raise e
            raise BrokerAPIError(str(e), "Angel One")

class GrowwBroker(BrokerInterface):
    def __init__(self, credentials: Dict[str, Any], user_id: Any = None):
        self.user_id = user_id
        self.api_key = credentials.get("API Key")
        self.secret = credentials.get("Secret")
        self.totp_secret = credentials.get("TOTP Secret")
        self.access_token = None
        self._groww = None

    def _get_client(self):
        try:
            if self._groww is None:
                if self.totp_secret:
                    totp = pyotp.TOTP(self.totp_secret).now()
                    self.access_token = GrowwAPI.get_access_token(api_key=self.api_key, totp=totp)
                elif self.secret:
                    self.access_token = GrowwAPI.get_access_token(api_key=self.api_key, secret=self.secret)
                else:
                    raise ValueError("Groww requires either TOTP Secret or Secret key")
                self._groww = GrowwAPI(self.access_token)
            return self._groww
        except Exception as e:
            raise BrokerAPIError(f"Authentication failed: {str(e)}", "Groww")

    def get_profile(self) -> Dict[str, Any]:
        try:
            return self._get_client().get_user_profile()
        except Exception as e:
            raise BrokerAPIError(str(e), "Groww")

    def get_balance(self) -> Dict[str, Any]:
        try:
            data = self._get_client().get_user_balance()
            return {
                "availablecash": data.get('availableBalance', 0),
                "net": data.get('openingBalance', 0),
                "utilised": data.get('utilizedBalance', 0)
            }
        except Exception as e:
            raise BrokerAPIError(str(e), "Groww")

    @cache_response(ttl=60)
    def get_positions(self) -> List[PositionSchema]:
        try:
            positions = self._get_client().get_positions()
            return [
                PositionSchema(
                    tradingsymbol=p.get('symbolName', p.get('tradingsymbol')),
                    exchange=p.get('exchange', 'NSE'),
                    product=p.get('product', 'CNC'),
                    quantity=int(p.get('quantity', 0)),
                    average_price=float(p.get('avgPrice', p.get('average_price', 0))),
                    last_price=float(p.get('ltp', p.get('last_price', 0))),
                    pnl=float(p.get('pnl', 0)),
                    realised=float(p.get('realisedPnl', p.get('realised', 0))),
                    unrealised=float(p.get('unrealisedPnl', p.get('unrealised', 0))),
                    buy_quantity=int(p.get('buyQty', p.get('buy_quantity', 0))),
                    sell_quantity=int(p.get('sellQty', p.get('sell_quantity', 0)))
                ) for p in positions
            ]
        except Exception as e:
            raise BrokerAPIError(str(e), "Groww")

    @cache_response(ttl=60)
    def get_holdings(self) -> List[HoldingSchema]:
        try:
            holdings = self._get_client().get_holdings_for_user()
            return [
                HoldingSchema(
                    tradingsymbol=h.get('symbolName', h.get('tradingsymbol')),
                    exchange=h.get('exchange', 'NSE'),
                    isin=h.get('isin', ''),
                    quantity=int(h.get('quantity', 0)),
                    average_price=float(h.get('avgPrice', h.get('average_price', 0))),
                    last_price=float(h.get('ltp', h.get('last_price', 0))),
                    pnl=float(h.get('pnl', 0)),
                    product=h.get('product', 'CNC'),
                    realised_quantity=int(h.get('realisedQty', h.get('realised_quantity', 0))),
                    t1_quantity=int(h.get('t1Qty', h.get('t1_quantity', 0)))
                ) for h in holdings
            ]
        except Exception as e:
            raise BrokerAPIError(str(e), "Groww")

    def get_trades(self) -> List[Dict[str, Any]]:
        return []

    def place_order(
        self,
        symbol: str,
        quantity: int,
        side: str,
        order_type: str,
        price: Optional[float] = None,
        product: str = "MIS",
        validity: str = "DAY"
    ) -> Dict[str, Any]:
        try:
            client = self._get_client()
            order_params = {
                "symbol": symbol,
                "quantity": quantity,
                "side": side.lower(),
                "type": order_type.lower(),
                "product": product,
                "validity": validity,
            }
            if price is not None:
                order_params["price"] = price
            response = client.place_order(order_params)
            return {
                "order_id": response.get("orderId"),
                "status": "placed",
                "broker": "Groww"
            }
        except Exception as e:
            raise BrokerAPIError(str(e), "Groww")

class DhanBroker(BrokerInterface):
    def __init__(self, credentials: Dict[str, Any], user_id: Any = None):
        self.user_id = user_id
        self.client_id = credentials.get("Client ID")
        self.access_token = credentials.get("Access Token")
        self._dhan = None

    def _get_client(self):
        try:
            if self._dhan is None:
                self._dhan = dhanhq(self.client_id, self.access_token)
            return self._dhan
        except Exception as e:
            raise BrokerAPIError(f"Initialization failed: {str(e)}", "Dhan")

    def get_profile(self) -> Dict[str, Any]:
        return {"client_id": self.client_id, "status": "connected"}

    def get_balance(self) -> Dict[str, Any]:
        try:
            data = self._get_client().get_fund_limits()
            # Dhan returns direct dict or wrapped in data
            res = data.get('data', data) if isinstance(data, dict) else {}
            return {
                "availablecash": res.get('availabelBalance', 0),
                "net": res.get('netDerivatives', 0),
                "utilised": res.get('utilizedAmount', 0)
            }
        except Exception as e:
            raise BrokerAPIError(str(e), "Dhan")

    @cache_response(ttl=60)
    def get_positions(self) -> List[PositionSchema]:
        try:
            response = self._get_client().get_positions()
            # Dhan SDK returns data in 'data' key or directly depending on version
            positions = response.get('data', response) if isinstance(response, dict) else response
            return [
                PositionSchema(
                    tradingsymbol=p.get('tradingsymbol'),
                    exchange=p.get('exchangeSegment', 'NSE'),
                    product=p.get('productType', 'CNC'),
                    quantity=int(p.get('netQty', 0)),
                    average_price=float(p.get('avgPrice', 0)),
                    last_price=float(p.get('lastPrice', 0)),
                    pnl=float(p.get('pnl', 0)),
                    realised=float(p.get('realizedProfit', 0)),
                    unrealised=float(p.get('unrealizedProfit', 0)),
                    buy_quantity=int(p.get('buyQty', 0)),
                    sell_quantity=int(p.get('sellQty', 0))
                ) for p in positions
            ]
        except Exception as e:
            raise BrokerAPIError(str(e), "Dhan")

    @cache_response(ttl=60)
    def get_holdings(self) -> List[HoldingSchema]:
        try:
            response = self._get_client().get_holdings()
            holdings = response.get('data', response) if isinstance(response, dict) else response
            return [
                HoldingSchema(
                    tradingsymbol=h.get('tradingsymbol'),
                    exchange=h.get('exchangeSegment', 'NSE'),
                    isin=h.get('isinCode', ''),
                    quantity=int(h.get('quantity', 0)),
                    average_price=float(h.get('avgCostPrice', 0)),
                    last_price=float(h.get('lastPrice', 0)),
                    pnl=float(h.get('pnl', 0)),
                    product=h.get('productType', 'CNC'),
                    realised_quantity=int(h.get('quantity', 0)),
                    t1_quantity=int(h.get('t1Quantity', 0))
                ) for h in holdings
            ]
        except Exception as e:
            raise BrokerAPIError(str(e), "Dhan")

    def get_trades(self) -> List[Dict[str, Any]]:
        try:
            return self._get_client().get_trade_book()
        except Exception as e:
            raise BrokerAPIError(str(e), "Dhan")

    def place_order(
        self,
        symbol: str,
        quantity: int,
        side: str,
        order_type: str,
        price: Optional[float] = None,
        product: str = "MIS",
        validity: str = "DAY"
    ) -> Dict[str, Any]:
        try:
            dhan_order = self._get_client().place_order(
                symbol=symbol,
                quantity=quantity,
                side=side,
                order_type=order_type,
                price=price,
                product=product,
                validity=validity,
            )
            return {
                "order_id": dhan_order.get("orderId"),
                "status": "placed",
                "broker": "Dhan"
            }
        except Exception as e:
            raise BrokerAPIError(str(e), "Dhan")

class UpstoxBroker(BrokerInterface):
    def __init__(self, credentials: Dict[str, Any], user_id: Any = None):
        self.user_id = user_id
        self.api_key = credentials.get("API Key")
        self.access_token = credentials.get("Access Token")
        self._configuration = None

    def _get_config(self):
        if self._configuration is None:
            self._configuration = upstox_client.Configuration()
            self._configuration.access_token = self.access_token
        return self._configuration

    def get_profile(self) -> Dict[str, Any]:
        try:
            api_client = upstox_client.ApiClient(self._get_config())
            return upstox_client.UserApi(api_client).get_profile("v2")
        except Exception as e:
            raise BrokerAPIError(str(e), "Upstox")

    def get_balance(self) -> Dict[str, Any]:
        try:
            api_client = upstox_client.ApiClient(self._get_config())
            response = upstox_client.UserApi(api_client).get_user_balance("v2")
            data = response.data if hasattr(response, 'data') else response
            # Upstox v2 returns dict or object with equity/commodity keys
            equity = data.get('equity', {}) if isinstance(data, dict) else getattr(data, 'equity', {})
            return {
                "availablecash": equity.get('available_margin', 0) if isinstance(equity, dict) else getattr(equity, 'available_margin', 0),
                "net": equity.get('net', 0) if isinstance(equity, dict) else getattr(equity, 'net', 0),
                "utilised": equity.get('used_margin', 0) if isinstance(equity, dict) else getattr(equity, 'used_margin', 0)
            }
        except Exception as e:
            raise BrokerAPIError(str(e), "Upstox")

    @cache_response(ttl=60)
    def get_positions(self) -> List[PositionSchema]:
        try:
            api_client = upstox_client.ApiClient(self._get_config())
            response = upstox_client.PortfolioApi(api_client).get_positions()
            # Upstox SDK returns response object, data is in .data
            positions = response.data if hasattr(response, 'data') else response
            return [
                PositionSchema(
                    tradingsymbol=getattr(p, 'tradingsymbol', p.get('tradingsymbol')),
                    exchange=getattr(p, 'exchange', p.get('exchange')),
                    product=getattr(p, 'product', p.get('product')),
                    quantity=int(getattr(p, 'quantity', p.get('quantity', 0))),
                    average_price=float(getattr(p, 'average_price', p.get('average_price', 0))),
                    last_price=float(getattr(p, 'last_price', p.get('last_price', 0))),
                    pnl=float(getattr(p, 'pnl', p.get('pnl', 0))),
                    realised=float(getattr(p, 'realised', p.get('realised', 0))),
                    unrealised=float(getattr(p, 'unrealised', p.get('unrealised', 0))),
                    buy_quantity=int(getattr(p, 'buy_quantity', p.get('buy_quantity', 0))),
                    sell_quantity=int(getattr(p, 'sell_quantity', p.get('sell_quantity', 0)))
                ) for p in positions
            ]
        except Exception as e:
            raise BrokerAPIError(str(e), "Upstox")

    @cache_response(ttl=60)
    def get_holdings(self) -> List[HoldingSchema]:
        try:
            api_client = upstox_client.ApiClient(self._get_config())
            response = upstox_client.PortfolioApi(api_client).get_holdings()
            holdings = response.data if hasattr(response, 'data') else response
            return [
                HoldingSchema(
                    tradingsymbol=getattr(h, 'tradingsymbol', h.get('tradingsymbol')),
                    exchange=getattr(h, 'exchange', h.get('exchange')),
                    isin=getattr(h, 'isin', h.get('isin', '')),
                    quantity=int(getattr(h, 'quantity', h.get('quantity', 0))),
                    average_price=float(getattr(h, 'average_price', h.get('average_price', 0))),
                    last_price=float(getattr(h, 'last_price', h.get('last_price', 0))),
                    pnl=float(getattr(h, 'pnl', h.get('pnl', 0))),
                    product=getattr(h, 'product', h.get('product', 'CNC')),
                    realised_quantity=int(getattr(h, 'realised_quantity', h.get('realised_quantity', 0))),
                    t1_quantity=int(getattr(h, 't1_quantity', h.get('t1_quantity', 0)))
                ) for h in holdings
            ]
        except Exception as e:
            raise BrokerAPIError(str(e), "Upstox")
        
    def get_trades(self) -> List[Dict[str, Any]]:
        try:
            api_client = upstox_client.ApiClient(self._get_config())
            return upstox_client.TradeApi(api_client).get_trades()
        except Exception as e:
            raise BrokerAPIError(str(e), "Upstox")

class BrokerFactory:
    @staticmethod
    def get_broker(broker_name: str, encrypted_creds: str, user_id: Any = None) -> BrokerInterface:
        creds = decrypt_credentials(encrypted_creds)
        name = broker_name.lower().replace(" ", "")
        if name == "zerodha":
            return ZerodhaBroker(creds, user_id)
        elif name == "angelone":
            return AngelOneBroker(creds, user_id)
        elif name == "groww":
            return GrowwBroker(creds, user_id)
        elif name == "dhan":
            return DhanBroker(creds, user_id)
        elif name == "upstox":
            return UpstoxBroker(creds, user_id)
        raise ValueError(f"Broker {broker_name} not supported yet")
