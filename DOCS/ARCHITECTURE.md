# Insight Engine - System Architecture

**Version:** 2.0  
**Date:** 2026-04-20

---

## High-Level Architecture

```
                                    ┌─────────────────┐
                                    │   Cloudflare    │
                                    │      SSL        │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │     Nginx       │
                                    │  Reverse Proxy  │
                                    │  (8081/8001)    │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
         ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
         │   Frontend       │    │    Backend       │    │    Database      │
         │   (Static)       │    │   (FastAPI)      │    │   (PostgreSQL)   │
         │   Port 8081      │    │   Port 8001      │    │   Port 5432      │
         └──────────────────┘    └────────┬─────────┘    └──────────────────┘
                                          │
                                          ▼
                                 ┌──────────────────┐
                                 │      Redis       │
                                 │   (Planned)      │
                                 └──────────────────┘
```

---

## Component Architecture

### Frontend (Native)

```
┌─────────────────────────────────────────────────────────────┐
│                    frontend_native/                          │
├─────────────────────────────────────────────────────────────┤
│  HTML Pages                                                  │
│  ├── index.html      - Landing page                         │
│  ├── login.html      - Authentication                       │
│  ├── register.html   - Registration                         │
│  ├── dashboard.html  - Main trading interface               │
│  └── admin.html      - Admin panel                          │
├─────────────────────────────────────────────────────────────┤
│  JavaScript Modules                                          │
│  ├── js/app.js       - Chart, broker grid, initialization   │
│  ├── js/api.js       - REST API client                      │
│  ├── js/auth.js      - Token management                     │
│  └── js/websocket.js - Real-time data handler               │
└─────────────────────────────────────────────────────────────┘
```

### Backend (FastAPI)

```
┌─────────────────────────────────────────────────────────────┐
│                    backend/app/                              │
├─────────────────────────────────────────────────────────────┤
│  main.py            - FastAPI application, CORS, routers    │
├─────────────────────────────────────────────────────────────┤
│  core/                                                       │
│  ├── config.py      - Settings (pydantic-settings)          │
│  ├── database.py    - SQLAlchemy engine, session factory    │
│  └── security.py    - JWT, password hashing                 │
├─────────────────────────────────────────────────────────────┤
│  api/                                                        │
│  ├── auth.py        - Login, register, password reset       │
│  ├── brokers.py     - Broker CRUD operations                │
│  ├── admin.py       - Admin endpoints                       │
│  └── ws.py          - WebSocket market data                 │
├─────────────────────────────────────────────────────────────┤
│  models/                                                     │
│  └── user.py        - User, BrokerCredential tables         │
├─────────────────────────────────────────────────────────────┤
│  services/          - Business logic layer (empty)          │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Authentication Flow

```
┌─────────┐         ┌─────────┐         ┌─────────┐         ┌─────────┐
│  User   │         │  Front  │         │  Back   │         │   DB    │
└────┬────┘         └────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │                   │
     │  1. Enter creds   │                   │                   │
     │──────────────────>│                   │                   │
     │                   │                   │                   │
     │  2. POST /login   │                   │                   │
     │                   │──────────────────>│                   │
     │                   │                   │                   │
     │                   │  3. Query user    │                   │
     │                   │                   │──────────────────>│
     │                   │                   │                   │
     │                   │  4. User record   │                   │
     │                   │<──────────────────│                   │
     │                   │                   │                   │
     │                   │  5. Verify pass   │                   │
     │                   │  6. Create JWT    │                   │
     │                   │                   │                   │
     │  7. Token + role  │                   │                   │
     │<──────────────────│                   │                   │
     │                   │                   │                   │
     │  8. Store token   │                   │                   │
     │<──────────────────│                   │                   │
```

### WebSocket Market Data Flow

```
┌─────────┐         ┌─────────┐         ┌─────────┐
│  Client │         │   WS    │         │  Market │
│         │         │ Server  │         │  Data   │
└────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │
     │  1. Connect WS    │                   │
     │──────────────────>│                   │
     │                   │                   │
     │  2. Accept        │                   │
     │<──────────────────│                   │
     │                   │                   │
     │                   │  3. Generate tick │
     │                   │<──────────────────│
     │                   │                   │
     │  4. Send tick     │                   │
     │<──────────────────│                   │
     │                   │                   │
     │  5. Update chart  │                   │
     │<──────────────────│                   │
     │                   │                   │
     │     (Repeat every 1 second)           │
```

### Broker Connection Flow (Planned)

```
┌─────────┐         ┌─────────┐         ┌─────────┐         ┌─────────┐
│  User   │         │  Front  │         │  Back   │         │ Broker  │
└────┬────┘         └────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │                   │
     │  1. Select broker │                   │                   │
     │──────────────────>│                   │                   │
     │                   │                   │                   │
     │  2. Enter creds   │                   │                   │
     │──────────────────>│                   │                   │
     │                   │                   │                   │
     │  3. POST creds    │                   │                   │
     │                   │──────────────────>│                   │
     │                   │                   │                   │
     │                   │  4. Encrypt       │                   │
     │                   │  5. Store in DB   │                   │
     │                   │──────────────────────────────────────>│
     │                   │                   │                   │
     │  6. Connected     │                   │                   │
     │<──────────────────│                   │                   │
```

---

## Security Architecture

### Current Implementation

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
├─────────────────────────────────────────────────────────────┤
│  Authentication                                              │
│  ├── JWT tokens (HS256 algorithm)                           │
│  ├── 30-minute expiry                                       │
│  └── Bearer token in Authorization header                   │
├─────────────────────────────────────────────────────────────┤
│  Password Security                                           │
│  ├── bcrypt hashing (12 rounds)                             │
│  └── passlib context                                        │
├─────────────────────────────────────────────────────────────┤
│  CORS                                                        │
│  └── Currently: allow_all (*) - NEEDS FIX                   │
└─────────────────────────────────────────────────────────────┘
```

### Planned Security Enhancements

```
┌─────────────────────────────────────────────────────────────┐
│              Planned Security Layers                         │
├─────────────────────────────────────────────────────────────┤
│  Rate Limiting                                               │
│  ├── 5 requests/minute for login                            │
│  └── 3 requests/hour for registration                       │
├─────────────────────────────────────────────────────────────┤
│  Credential Encryption                                       │
│  ├── AES-256 (Fernet) for broker credentials                │
│  └── Key stored in environment variable                     │
├─────────────────────────────────────────────────────────────┤
│  Password Reset                                              │
│  ├── Redis token storage with TTL                           │
│  └── Email delivery via SMTP                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────────────┐          ┌─────────────────────────┐
│         Users           │          │   BrokerCredentials     │
├─────────────────────────┤          ├─────────────────────────┤
│ PK  id                  │◄────────┤│ FK  user_id             │
│     username (UNIQ)     │          │     broker_name         │
│     email (UNIQ)        │          │     credentials (JSON)  │
│     mobile_no           │          │     is_active           │
│     hashed_password     │          └─────────────────────────┘
│     role (ENUM)         │
│     is_active           │
└─────────────────────────┘
```

### Planned Tables

```
┌─────────────────────────┐          ┌─────────────────────────┐
│       MarketData        │          │      Watchlists         │
├─────────────────────────┤          ├─────────────────────────┤
│ PK  id                  │          ├─────────────────────────┤
│     symbol              │          │ FK  user_id             │
│     timestamp           │          │     symbol              │
│     open                │          │     created_at          │
│     high                │          └─────────────────────────┘
│     low                 │
│     close               │
│     volume              │
└─────────────────────────┘
```

---

## Deployment Architecture

### Current (Native)

```
┌─────────────────────────────────────────────────────────────┐
│                    Single Server                             │
├─────────────────────────────────────────────────────────────┤
│  Nginx (systemd)                                             │
│  ├── insight-engine site config                             │
│  └── Reverse proxy to 8081/8001                             │
├─────────────────────────────────────────────────────────────┤
│  Backend (systemd: insight-backend)                          │
│  ├── uvicorn worker                                         │
│  └── Port 8001                                              │
├─────────────────────────────────────────────────────────────┤
│  Frontend (static files)                                     │
│  └── Served via Nginx port 8081                             │
├─────────────────────────────────────────────────────────────┤
│  Database (SQLite file)                                      │
│  └── /path/to/insight_engine.db                             │
└─────────────────────────────────────────────────────────────┘
```

### Target (Docker)

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose                            │
├─────────────────────────────────────────────────────────────┤
│  Container: nginx                                            │
│  ├── Ports: 80, 443                                          │
│  └── SSL termination                                         │
├─────────────────────────────────────────────────────────────┤
│  Container: backend                                          │
│  ├── FastAPI + uvicorn                                       │
│  └── Health check endpoint                                   │
├─────────────────────────────────────────────────────────────┤
│  Container: frontend                                         │
│  ├── Built static assets                                     │
│  └── Served via nginx                                        │
├─────────────────────────────────────────────────────────────┤
│  Container: db (timescaledb)                                 │
│  ├── PostgreSQL 15 + TimescaleDB                             │
│  └── Persistent volume                                       │
├─────────────────────────────────────────────────────────────┤
│  Container: redis                                            │
│  ├── Session storage                                         │
│  └── Cache layer                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## API Gateway (Nginx) Configuration

### Current Routing

```
Request Path              →    Target
─────────────────────────────────────
/                         →    frontend_native/ (8081)
/*.html                   →    frontend_native/ (8081)
/api/*                    →    backend (8001)
/api/ws/*                 →    backend WebSocket (8001)
```

### Nginx Config Highlights

```nginx
# Backend API proxy
location /api/ {
    proxy_pass http://localhost:8001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}

# Frontend static
location / {
    proxy_pass http://localhost:8081;
}
```

---

## Scalability Considerations

### Current Limitations

| Component | Limitation | Solution |
|-----------|------------|----------|
| Database | SQLite single-writer | Migrate to PostgreSQL |
| Cache | None | Add Redis layer |
| WebSocket | Direct client-server | Add Redis pub/sub |
| Rate Limiting | None | Add slowapi |
| Sessions | In-memory | Redis session store |

### Horizontal Scaling Path

1. **Database:** PostgreSQL with read replicas
2. **Cache:** Redis cluster for session/data caching
3. **Backend:** Multiple uvicorn workers behind Nginx
4. **WebSocket:** Redis pub/sub for cross-instance messaging
