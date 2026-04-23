# Changelog

All notable changes to Insight Engine are documented here.

---

## [3.0] - 2026-04-21

### Added
- **FINAL_POA.md** - Comprehensive phase-wise implementation plan
- **README.md** - Complete project documentation
- **DOCS/BROKER_INTEGRATION.md** - Broker-specific integration guides
- **DOCS/FUNCTION_SPEC.md** - Detailed function specifications
- **backend/app/schemas/** - Pydantic schemas for API validation
  - `auth.py` - Auth schemas (UserCreate, LoginRequest, etc.)
  - `broker.py` - Broker schemas (BrokerCreate, HoldingsItem, etc.)
  - `common.py` - Shared schemas (BaseResponse, HealthCheckResponse)
- **scripts/** - Utility scripts
  - `setup_dev.sh` - Development environment setup
  - `migrate_db.sh` - Database migration helper
  - `health_check.sh` - Service health monitoring
- **.env.example** - Environment variable template

### Improved
- **backend/app/main.py** - Added comprehensive module docstring
- **backend/app/api/auth.py** - Added comprehensive module docstring
- **backend/app/services/broker_factory.py** - Added comprehensive module docstring

### Phase Status
- Phase 1 (Banking): Ready to start
- Phase 2 (Grow): Planned
- Phase 3 (Zero-to-Hero): Planned

---

## [2.0] - 2026-04-20

### Added
- **frontend_native/** - Native HTML/JS frontend
  - `index.html`, `login.html`, `register.html`, `dashboard.html`, `admin.html`
  - `js/app.js` - Chart and broker grid logic
  - `js/api.js` - REST API client
  - `js/auth.js` - Token management
  - `js/websocket.js` - Real-time data handler
- **backend/app/services/broker_factory.py** - Unified broker interface
- **DOCS/** - Comprehensive documentation
  - `ARCHITECTURE.md` - System design
  - `API_REFERENCE.md` - Endpoint documentation
  - `DEPLOYMENT.md` - Deployment guide
  - `FUNCTIONALITY.md` - Feature documentation
  - `PROJECT_STATUS.md` - Project health
  - `POA_INSIGHT.md` - Legacy POA (superseded by FINAL_POA.md)

### Changed
- Migrated from React to Native HTML/JS frontend
- PostgreSQL support (previously SQLite only)
- Redis integration for password reset tokens

### Features
- JWT authentication with rate limiting
- 5 broker configurations (Zerodha, Angel One, Groww, Dhan, Upstox)
- WebSocket market data streaming (simulated NIFTY 50)
- AES-256 credential encryption

---

## [1.0] - 2026-04-08

### Added
- Initial FastAPI backend
- User authentication system (registration, login)
- Broker credential storage
- Basic admin panel

### Structure
```
backend/
├── app/
│   ├── main.py
│   ├── api/auth.py
│   ├── core/config.py, database.py, security.py
│   └── models/user.py
└── requirements.txt
```

---

## Old Project (`/home/old project/insight_engine/`)

### Structure
- Legacy monolithic design
- SQLite database (`db/market.db`)
- Angel One only (`test_angel_one.py`)
- Setup scripts: `setup_all_in_one.sh`, `setup_full.sh`
- File-based output: `outputs/by_date/YYYY/MM/DD/`

### Status
- Archived, not in use
- Reference for legacy functionality

---

*End of changelog*