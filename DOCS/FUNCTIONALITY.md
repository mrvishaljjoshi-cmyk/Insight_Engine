# Insight Engine - Functionality Documentation

**Version:** 2.0  
**Last Updated:** 2026-04-20

---

## Table of Contents

1. [System Overview](#system-overview)
2. [User Features](#user-features)
3. [Admin Features](#admin-features)
4. [API Reference](#api-reference)
5. [Frontend Pages](#frontend-pages)

---

## System Overview

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Insight Engine                          │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Native HTML/JS)    │  Backend (FastAPI)          │
│  - Tailwind CSS               │  - REST API                 │
│  - Lightweight Charts         │  - WebSocket Server         │
│  - Vanilla JS                 │  - SQLAlchemy ORM           │
├─────────────────────────────────────────────────────────────┤
│                    Database (SQLite/PostgreSQL)              │
│                    Cache (Redis - Planned)                   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | HTML5, Tailwind CSS 3.x | UI styling |
| Frontend | Vanilla ES6 JavaScript | Client logic |
| Charts | Lightweight Charts 4.x | Candlestick visualization |
| Backend | Python 3.12 | Runtime |
| Backend | FastAPI 0.109+ | Web framework |
| Auth | python-jose | JWT tokens |
| Security | passlib[bcrypt] | Password hashing |
| Database | SQLAlchemy 2.x | ORM |
| Database | PostgreSQL 15 / SQLite | Data persistence |
| Cache | Redis 7.x | Session storage (planned) |

---

## User Features

### 1. Authentication

#### Registration
- **Endpoint:** `POST /api/auth/register`
- **Fields:** username, email, password, mobile_no (optional)
- **Validation:** Email format, unique username/email
- **Response:** User created confirmation

#### Login
- **Endpoint:** `POST /api/auth/login`
- **Fields:** username_or_email, password
- **Response:** JWT token, role, username, token_type

#### Password Reset
- **Request:** `POST /api/auth/password-reset-request`
- **Confirm:** `POST /api/auth/password-reset-confirm`
- **Note:** Currently returns debug token (no email)

### 2. Broker Management

#### Connect Broker
- **Endpoint:** `POST /api/brokers/`
- **Body:** broker_name, credentials (object)
- **Supported Brokers:**
  - Zerodha (API Key, API Secret, Client ID, TOTP Secret)
  - Angel One (SmartAPI Key, Client ID, Password, TOTP Secret)
  - Groww (API Key, API Secret)
  - Dhan (Client ID, Access Token)
  - Upstox (API Key, API Secret, Redirect URI)

#### View Connected Brokers
- **Endpoint:** `GET /api/brokers/`
- **Response:** Array of broker connections

#### Disconnect Broker
- **Endpoint:** `DELETE /api/brokers/{id}`
- **Response:** Confirmation message

### 3. Market Data

#### Live WebSocket
- **Endpoint:** `ws://{host}/api/ws/market-data`
- **Data:** Symbol, price, timestamp
- **Frequency:** 1 second intervals
- **Current Symbol:** NIFTY 50 (simulated)

---

## Admin Features

### Admin Dashboard
- **Access:** `/admin.html`
- **Features:**
  - User list management
  - System statistics
  - Broker connection overview

### Admin API Endpoints
- **Endpoint:** `GET /api/admin/users`
- **Access:** Admin role required
- **Response:** List of all users

---

## API Reference

### Base URL
- Development: `http://localhost:8001`
- Production: `https://insight.vjprojects.co.in`

### Authentication Endpoints

```
POST   /api/auth/register          Register new user
POST   /api/auth/login             User login
POST   /api/auth/password-reset-request    Request reset
POST   /api/auth/password-reset-confirm    Confirm reset
```

### Broker Endpoints

```
POST   /api/brokers/               Add broker credential
GET    /api/brokers/               List all brokers
DELETE /api/brokers/{id}           Delete broker
```

### Admin Endpoints

```
GET    /api/admin/users            List all users
```

### WebSocket Endpoints

```
WS     /api/ws/market-data         Real-time market ticks
```

### Health Check

```
GET    /                           API status
```

---

## Frontend Pages

### Public Pages

| Page | Path | Description |
|------|------|-------------|
| Landing | `/index.html` | Welcome page, feature overview |
| Login | `/login.html` | User authentication form |
| Register | `/register.html` | New user registration |

### Protected Pages

| Page | Path | Description | Auth Required |
|------|------|-------------|---------------|
| Dashboard | `/dashboard.html` | Main trading interface | Yes |
| Admin Panel | `/admin.html` | Admin management | Admin only |

---

## Database Schema

### Users Table

| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PRIMARY KEY, INDEX |
| username | String | UNIQUE, INDEX, NOT NULL |
| email | String | UNIQUE, INDEX, NOT NULL |
| mobile_no | String | NULLABLE |
| hashed_password | String | NOT NULL |
| role | Enum | Admin/Trader/Developer |
| is_active | Boolean | DEFAULT true |

### Broker Credentials Table

| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PRIMARY KEY, INDEX |
| user_id | Integer | FOREIGN KEY (users) |
| broker_name | String | NOT NULL |
| credentials | JSON | NOT NULL |
| is_active | Boolean | DEFAULT true |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | JWT signing key | (required) |
| DATABASE_URL | Database connection string | sqlite:///./insight_engine.db |
| GOOGLE_CLIENT_ID | OAuth client ID | None |
| REDIS_HOST | Redis server host | localhost |
| REDIS_PORT | Redis server port | 6379 |

---

## File Locations

### Backend
```
backend/
├── app/main.py              # Application entry
├── app/core/config.py       # Settings
├── app/core/database.py     # DB connection
├── app/core/security.py     # Auth utilities
├── app/api/auth.py          # Auth routes
├── app/api/brokers.py       # Broker routes
├── app/api/ws.py            # WebSocket routes
└── app/models/user.py       # DB models
```

### Frontend
```
frontend_native/
├── index.html               # Landing
├── login.html               # Login
├── register.html            # Register
├── dashboard.html           # Dashboard
├── admin.html               # Admin
└── js/
    ├── app.js               # Main logic
    ├── api.js               # API calls
    ├── auth.js              # Auth handling
    └── websocket.js         # WS handling
```
