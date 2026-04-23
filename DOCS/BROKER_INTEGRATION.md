# Broker Integration Guide

**Version:** 1.0 | **Last Updated:** 2026-04-21

---

## Overview

Insight Engine supports integration with the top 5 Indian brokers through a unified factory pattern. Each broker has its own SDK and authentication method, but the `BrokerFactory` abstracts them into a common interface.

## Supported Brokers

| Broker | API | SDK | Auth Method |
|--------|-----|-----|-------------|
| Zerodha | Kite Connect | `kiteconnect` | API Key + Access Token |
| Angel One | SmartAPI | `SmartApi` | API Key + TOTP |
| Groww | GrowwAPI | `growwapi` | API Key + Secret/TOTP |
| Dhan | DhanHQ | `dhanhq` | Client ID + Access Token |
| Upstox | Upstox Client | `upstox_client` | API Key + Access Token |

---

## Zerodha (Kite Connect)

### Credentials Required

| Field | Description | Where to Get |
|-------|-------------|--------------|
| API Key | Your Kite Connect API key | [developers.kite.trade](https://developers.kite.trade) |
| API Secret | Your Kite Connect API secret | Same as above |
| Client ID | Your Zerodha client ID | Zerodha console |
| TOTP Secret | Secret for generating TOTP | Enable 2FA in Zerodha |

### Setup Steps

1. Register at [Kite Connect](https://developers.kite.trade)
2. Create an app to get API Key and Secret
3. Enable 2FA and get TOTP secret from Zerodha
4. Generate access token via login flow
5. Store access token securely in the app

### API Reference

```python
from app.services.broker_factory import BrokerFactory

# Initialize broker
broker = BrokerFactory.get_broker("Zerodha", encrypted_credentials)

# Get profile
profile = broker.get_profile()

# Get margins/balance
margins = broker.get_balance()

# Get positions
positions = broker.get_positions()

# Get holdings
holdings = broker.get_holdings()

# Place order (Phase 2)
order = broker.place_order(symbol, quantity, side, order_type, price)
```

---

## Angel One (SmartAPI)

### Credentials Required

| Field | Description | Where to Get |
|-------|-------------|--------------|
| SmartAPI Key | Angel One API key | [SmartAPI portal](https://smartapi.angelone.in) |
| Client ID | Your Angel One client ID | Angel One app |
| Password | Your Angel One password | Angel One app |
| TOTP Secret | Secret for TOTP | Enable 2FA in Angel One |

### Setup Steps

1. Register at [Angel One SmartAPI](https://smartapi.angelone.in)
2. Generate API key from portal
3. Enable 2FA and get TOTP secret
4. Use SmartAPI SDK for authentication

### API Reference

```python
from app.services.broker_factory import BrokerFactory

broker = BrokerFactory.get_broker("Angel One", encrypted_credentials)

# Login generates session (handled automatically)
profile = broker.get_profile()
margins = broker.get_balance()
positions = broker.get_positions()
holdings = broker.get_holdings()
```

---

## Groww

### Credentials Required

| Field | Description | Where to Get |
|-------|-------------|--------------|
| API Key | Groww API key | Groww developer portal |
| Secret | API secret (alternative to TOTP) | Groww developer portal |
| TOTP Secret | For 2FA enabled accounts | Groww app settings |

### Setup Steps

1. Register at Groww developer portal
2. Create app to get API Key and Secret
3. If using TOTP, enable 2FA in Groww app

### API Reference

```python
broker = BrokerFactory.get_broker("Groww", encrypted_credentials)
profile = broker.get_profile()
balance = broker.get_balance()
positions = broker.get_positions()
holdings = broker.get_holdings()
```

---

## Dhan

### Credentials Required

| Field | Description | Where to Get |
|-------|-------------|--------------|
| Client ID | Your Dhan client ID | Dhan trading platform |
| Access Token | Your Dhan access token | Dhan API settings |

### Setup Steps

1. Register at [Dhan](https://dhan.in)
2. Go to Settings → API → Create API Key
3. Generate access token
4. Store securely

### API Reference

```python
broker = BrokerFactory.get_broker("Dhan", encrypted_credentials)
balance = broker.get_balance()
positions = broker.get_positions()
holdings = broker.get_holdings()
```

---

## Upstox

### Credentials Required

| Field | Description | Where to Get |
|-------|-------------|--------------|
| API Key | Upstox API key | [Upstox developer portal](https://upstox.com/developer) |
| Access Token | Your Upstox access token | Upstox console |

### Setup Steps

1. Register at [Upstox Developer](https://upstox.com/developer)
2. Create app to get API Key
3. Generate access token via OAuth flow
4. Store access token securely

### API Reference

```python
broker = BrokerFactory.get_broker("Upstox", encrypted_credentials)
profile = broker.get_profile()
balance = broker.get_balance()
positions = broker.get_positions()
holdings = broker.get_holdings()
```

---

## Credential Encryption

All broker credentials are encrypted using Fernet (AES-256) before storage:

```python
from app.core.security import encrypt_credentials, decrypt_credentials

# Encrypt credentials before storing
encrypted = encrypt_credentials({
    "api_key": "...",
    "access_token": "..."
})

# Decrypt when needed
creds = decrypt_credentials(encrypted)
```

### Masking for Display

Credentials are masked before returning to frontend:

```python
from app.core.security import mask_credentials

masked = mask_credentials({
    "api_key": "abcd1234efgh5678",
    "access_token": "xyz987654321"
})
# Returns: {"api_key": "ab***78", "access_token": "xy***21"}
```

---

## Broker Factory Usage

```python
from app.services.broker_factory import BrokerFactory, BrokerInterface

# Get a broker instance
broker = BrokerFactory.get_broker(broker_name, encrypted_credentials)

# All brokers implement BrokerInterface:
class BrokerInterface:
    def get_profile(self) -> dict
    def get_balance(self) -> dict
    def get_positions(self) -> dict
    def get_holdings(self) -> dict
    def place_order(self, symbol, quantity, side, order_type, price=None) -> dict
```

---

## Error Handling

Each broker may throw specific exceptions:

```python
try:
    broker = BrokerFactory.get_broker("Zerodha", creds)
    holdings = broker.get_holdings()
except ValueError as e:
    # Unknown broker
    print(f"Broker not supported: {e}")
except Exception as e:
    # API error
    print(f"Broker API error: {e}")
```

---

## Connection Status

Broker connection status can be checked:

```python
from app.services.broker_factory import BrokerFactory

status = BrokerFactory.get_connection_status(broker_id)
# Returns: "connected", "disconnected", "error"
```

---

## Next Steps

- **Phase 1:** Full Zerodha integration with live data
- **Phase 2:** All 5 brokers with order placement
- **Phase 3:** Production hardening and monitoring