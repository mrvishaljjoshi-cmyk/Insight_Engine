# Insight Engine 3.0
## Professional Indian Trading Platform

**Version:** 3.0 | **Status:** Active Development | **Stack:** FastAPI + Native HTML/JS

---

## Overview

Insight Engine is a professional-grade trading platform that provides unified access to multiple Indian brokers through a single interface. Built with FastAPI for the backend and native HTML/JS for the frontend, it offers real-time market data, secure broker integration, and comprehensive portfolio management.

### Key Features

- **Multi-Broker Support**: Connect to top 5 Indian brokers (Zerodha, Angel One, Groww, Dhan, Upstox)
- **Real-Time Data**: WebSocket-based live market data streaming
- **Secure Storage**: AES-256 encrypted broker credentials
- **JWT Authentication**: Secure token-based auth with rate limiting
- **Portfolio Management**: Track holdings, positions, and P&L across brokers
- **Native Frontend**: Lightweight, fast-loading dashboard without heavy frameworks

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Cloudflare SSL                             │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            Nginx Proxy                               │
│                         (Ports: 8081/8001)                           │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
           ┌────────────┐  ┌─────────────┐  ┌───────────┐
           │  Frontend  │  │   Backend   │  │   Redis   │
           │  (Static)  │  │  (FastAPI)  │  │   Cache   │
           │  Port 8081 │  │  Port 8001  │  │  Port 6379│
           └────────────┘  └──────┬──────┘  └───────────┘
                                   │
                                   ▼
                           ┌───────────────┐
                           │  PostgreSQL  │
                           │  Port 5432   │
                           └───────────────┘
```

---

## Project Structure

```
/home/VJPROJECTS/Insight_Engine/
├── CLAUDE.md                 # AI coding rules
├── FINAL_POA.md             # Master plan (phase-wise)
├── README.md                 # This file
│
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry
│   │   ├── api/             # API routes
│   │   ├── core/            # Config, DB, Security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── alembic/             # DB migrations
│   └── requirements.txt
│
├── frontend_native/          # Native HTML/JS frontend
│   ├── index.html           # Landing
│   ├── login.html           # Auth
│   ├── register.html        # Registration
│   ├── dashboard.html       # Main trading interface
│   ├── admin.html            # Admin panel
│   └── js/                  # JavaScript modules
│       ├── app.js           # Main app logic
│       ├── api.js           # API client
│       ├── auth.js          # Auth handling
│       └── websocket.js     # Real-time data
│
├── scripts/                  # Utility scripts
│   ├── setup_dev.sh        # Dev environment setup
│   ├── health_check.sh      # Health monitoring
│   └── migrate_db.sh        # Database migrations
│
├── docker/                   # Docker configs
├── tests/                   # Test suite
└── DOCS/                    # Documentation
    ├── ARCHITECTURE.md      # System design
    ├── API_REFERENCE.md     # API endpoints
    ├── BROKER_INTEGRATION.md # Broker setup guides
    ├── DEPLOYMENT.md        # Deployment guide
    └── CHANGELOG.md         # Version history
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js (optional, for frontend building)
- PostgreSQL 15+ (or use SQLite for dev)
- Redis 7+ (optional)

### Setup

```bash
# 1. Navigate to project
cd /home/VJPROJECTS/Insight_Engine

# 2. Run development setup
./scripts/setup_dev.sh

# 3. Configure environment
cp .env.example .env
# Edit .env with your SECRET_KEY and ENCRYPTION_KEY

# 4. Run database migrations
./scripts/migrate_db.sh up

# 5. Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 6. Start frontend (separate terminal)
cd frontend_native
python3 -m http.server 8081
```

### Access

- Frontend: http://localhost:8081
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

---

## Top 5 Indian Brokers

| Rank | Broker | API | Status |
|------|--------|-----|--------|
| 1 | **Zerodha** | Kite Connect | UI ✅ API ⚠️ |
| 2 | **Angel One** | SmartAPI | UI ✅ API ⚠️ |
| 3 | **Groww** | GrowwAPI | UI ✅ API ⚠️ |
| 4 | **Dhan** | DhanHQ | UI ✅ API ⚠️ |
| 5 | **Upstox** | Upstox Client | UI ✅ API ⚠️ |

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login, returns JWT |
| POST | `/auth/register` | Create account |
| GET | `/auth/me` | Get current user |
| PATCH | `/auth/me` | Update profile |
| DELETE | `/auth/me` | Delete account |
| POST | `/auth/change-password` | Change password |
| POST | `/auth/password-reset-request` | Request reset |
| POST | `/auth/password-reset-confirm` | Confirm reset |

### Brokers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/brokers/` | List connected brokers |
| POST | `/brokers/` | Add broker connection |
| GET | `/brokers/{id}` | Get broker details |
| DELETE | `/brokers/{id}` | Remove broker |
| PATCH | `/brokers/{id}/toggle` | Enable/disable |
| GET | `/brokers/{id}/holdings` | Get holdings |
| GET | `/brokers/{id}/positions` | Get positions |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://host/api/ws/market-data` | Real-time market ticks |

---

## Phase-wise Development

### Phase 1: Banking (Weeks 1-4)
- Zerodha full integration
- Dashboard with real data
- Basic documentation

### Phase 2: Grow (Weeks 5-8)
- All 5 brokers integrated
- Order placement
- Multi-symbol support

### Phase 3: Zero-to-Hero (Weeks 9-12)
- Security hardening
- Performance optimization
- Production deployment

---

## Security

- JWT tokens with 30-minute expiry
- bcrypt password hashing (12 rounds)
- Fernet (AES-256) credential encryption
- Rate limiting on auth endpoints
- CORS whitelist protection
- Redis token storage with TTL

---

## Documentation

For detailed documentation, see:

- [FINAL_POA.md](FINAL_POA.md) - Master implementation plan
- [DOCS/ARCHITECTURE.md](DOCS/ARCHITECTURE.md) - System design
- [DOCS/API_REFERENCE.md](DOCS/API_REFERENCE.md) - API endpoints
- [DOCS/BROKER_INTEGRATION.md](DOCS/BROKER_INTEGRATION.md) - Broker setup
- [DOCS/DEPLOYMENT.md](DOCS/DEPLOYMENT.md) - Deployment guide

---

## License

Proprietary - All rights reserved