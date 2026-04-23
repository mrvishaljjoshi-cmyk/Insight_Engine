# Function Specification - Insight Engine 3.0

**Version:** 3.0 | **Date:** 2026-04-21

---

## 1. System Overview

### 1.1 Purpose

Insight Engine is a professional trading platform that provides unified access to multiple Indian brokers through a single dashboard interface. It enables traders to manage portfolios, view real-time market data, and track positions across different broker accounts.

### 1.2 Target Users

- Retail traders in India
- Active investors managing multiple broker accounts
- Traders requiring consolidated portfolio view

### 1.3 Core Value Proposition

Single dashboard for multiple brokers, real-time data, secure credential storage.

---

## 2. User Features

### 2.1 Authentication

| Feature | Description | Priority |
|---------|-------------|----------|
| User Registration | Email, username, password with validation | P0 |
| Login | Username/email + password, returns JWT | P0 |
| JWT Token Management | 30-min expiry, refresh on use | P0 |
| Password Change | Authenticated users can change password | P1 |
| Password Reset | Redis-based token flow (email pending) | P2 |
| Account Deletion | Users can delete their account | P1 |

### 2.2 Broker Management

| Feature | Description | Priority |
|---------|-------------|----------|
| Connect Broker | Add broker credentials (encrypted) | P0 |
| List Brokers | View all connected brokers | P0 |
| Disconnect Broker | Remove broker connection | P0 |
| Toggle Broker | Enable/disable broker without removing | P1 |
| Get Holdings | Fetch holdings from broker | P0 |
| Get Positions | Fetch open positions from broker | P0 |
| Get Balance | Fetch account balance/limits | P0 |

### 2.3 Market Data

| Feature | Description | Priority |
|---------|-------------|----------|
| WebSocket Streaming | Real-time tick data | P0 |
| Candlestick Charts | OHLCV visualization | P0 |
| Multi-Symbol | NIFTY, BANKNIFTY, FINNIFTY support | P2 |
| Historical Data | OHLCV storage and retrieval | P3 |

### 2.4 Portfolio Management

| Feature | Description | Priority |
|---------|-------------|----------|
| Consolidated Holdings | View across all brokers | P1 |
| Position Tracking | Open positions with P&L | P1 |
| P&L Calculation | Real-time profit/loss | P2 |
| Export Reports | Excel/PDF generation | P3 |

---

## 3. Admin Features

| Feature | Description | Priority |
|---------|-------------|----------|
| User List | View all registered users | P1 |
| Toggle User Status | Enable/disable user accounts | P2 |
| System Health | API/database/redis status | P1 |

---

## 4. Security Features

| Feature | Description | Priority |
|---------|-------------|----------|
| JWT Auth | HS256, 30-min expiry | P0 |
| Password Hashing | bcrypt, 12 rounds | P0 |
| Credential Encryption | Fernet (AES-256) | P0 |
| Rate Limiting | slowapi on auth endpoints | P0 |
| CORS Protection | Whitelist-based | P0 |
| Token Masking | Hide sensitive data in responses | P0 |

---

## 5. API Endpoints

### 5.1 Authentication

```
POST   /auth/login                    → {token, user}
POST   /auth/register                 → {user_id}
GET    /auth/me                       → {user}
PATCH  /auth/me                       → {user}
DELETE /auth/me                       → {message}
POST   /auth/change-password          → {message}
POST   /auth/password-reset-request   → {message}
POST   /auth/password-reset-confirm   → {message}
POST   /auth/logout                   → {message}
```

### 5.2 Brokers

```
GET    /brokers/                      → [{broker}]
POST   /brokers/                      → {broker}
GET    /brokers/{id}                  → {broker}
DELETE /brokers/{id}                  → {message}
PATCH  /brokers/{id}/toggle           → {broker}
GET    /brokers/{id}/holdings          → {holdings}
GET    /brokers/{id}/positions        → {positions}
GET    /brokers/{id}/balance          → {balance}
GET    /brokers/{id}/orders           → {orders} (Phase 2)
POST   /brokers/{id}/orders/          → {order} (Phase 2)
```

### 5.3 WebSocket

```
WS     /api/ws/market-data            → tick data stream
```

### 5.4 Admin

```
GET    /admin/users                   → [{user}]
POST   /admin/users                  → {user}
POST   /admin/users/{id}/toggle      → {user}
```

### 5.5 Health

```
GET    /                              → {name, status, timestamp}
GET    /health                        → {status, components}
GET    /api/protected                 → {message} (auth required)
```

---

## 6. Data Models

### 6.1 User

| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer | PK, auto-increment |
| username | String(50) | Unique, not null |
| email | String(255) | Unique, not null |
| mobile_no | String(20) | Nullable |
| hashed_password | String(255) | Not null |
| role | Enum | admin/trader/developer, default=trader |
| is_active | Boolean | default=true |
| created_at | DateTime | auto |
| updated_at | DateTime | auto-update |

### 6.2 BrokerCredential

| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer | PK, auto-increment |
| user_id | Integer | FK → users.id |
| broker_name | String(50) | Not null |
| credentials | Text | Encrypted JSON |
| is_active | Boolean | default=true |
| created_at | DateTime | auto |
| updated_at | DateTime | auto-update |

---

## 7. Technical Requirements

### 7.1 Backend

- Python 3.12+
- FastAPI 0.109+
- SQLAlchemy 2.x
- PostgreSQL 15 / SQLite (dev)
- Redis 7.x
- Pydantic v2

### 7.2 Frontend

- Native HTML5/ES6+
- Tailwind CSS 3.x
- Lightweight Charts 4.x
- No heavy frameworks (keep lightweight)

### 7.3 Infrastructure

- Nginx reverse proxy
- Cloudflare SSL
- systemd services

---

## 8. Non-Functional Requirements

### 8.1 Performance

- API response time: <100ms
- WebSocket latency: <500ms
- Support 100+ concurrent users

### 8.2 Security

- JWT expiry: 30 minutes
- Password hashing: bcrypt 12 rounds
- Encryption: AES-256 (Fernet)
- Rate limit: 10 req/min on login

### 8.3 Reliability

- Database migrations via Alembic
- Health check endpoint
- Redis session backup

---

## 9. Out of Scope (Phase 3)

- Actual order placement (Phase 2)
- Automated trading strategies
- Mobile app
- Multi-language support
- Social features

---

## 10. Dependencies

### Python Packages

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
pydantic>=2.0
pydantic-settings>=2.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
cryptography>=41.0.0
slowapi>=0.1.9
redis>=5.0.0
alembic>=1.13.0
psycopg2-binary>=2.9.9
pyotp>=2.9.0
kiteconnect>=4.0.0
smartapi-python>=1.3.0
growwapi>=0.1.0
dhanhq>=1.0.0
upstox_client>=3.0.0
```

---

*Document Version: 3.0*
*Last Updated: 2026-04-21*