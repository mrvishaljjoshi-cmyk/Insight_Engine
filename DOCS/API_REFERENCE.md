# Insight Engine - API Reference

**Base URL:** `http://localhost:8001/api`  
**Authentication:** Bearer token in `Authorization` header

---

## Authentication Endpoints

### POST /auth/register

Register a new user account.

**Request:**
```json
{
  "username": "trader123",
  "email": "trader@example.com",
  "password": "SecurePass123!",
  "mobile_no": "+91-9876543210"
}
```

**Response (200):**
```json
{
  "message": "User created successfully"
}
```

**Errors:**
- `400` - Username already registered
- `400` - Email already registered
- `422` - Validation error (invalid email format)

---

### POST /auth/login

Authenticate user and receive JWT token.

**Request:**
```json
{
  "username_or_email": "trader123",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "Trader",
  "username": "trader123",
  "token_type": "bearer"
}
```

**Errors:**
- `400` - Incorrect credentials
- `400` - Inactive user

---

### POST /auth/password-reset-request

Request a password reset token.

**Request:**
```json
{
  "email": "trader@example.com"
}
```

**Response (200):**
```json
{
  "message": "Reset link generated",
  "debug_token": "random_token_string"
}
```

**Note:** In production, token is sent via email. Currently returned for debugging.

**Errors:**
- `404` - User not found

---

### POST /auth/password-reset-confirm

Reset password with token.

**Request:**
```json
{
  "token": "random_token_string",
  "new_password": "NewSecurePass123!"
}
```

**Response (200):**
```json
{
  "message": "Password updated successfully"
}
```

**Errors:**
- `400` - Invalid or expired token

---

## Broker Endpoints

### POST /brokers/

Add a new broker credential.

**Request:**
```json
{
  "broker_name": "Zerodha",
  "credentials": {
    "API Key": "your_api_key",
    "API Secret": "your_api_secret",
    "Client ID": "your_client_id",
    "TOTP Secret": "your_totp_secret"
  }
}
```

**Response (200):**
```json
{
  "id": 1,
  "broker_name": "Zerodha",
  "is_active": true,
  "credentials": {
    "API Key": "your_api_key",
    ...
  }
}
```

**Errors:**
- `404` - User not found

---

### GET /brokers/

List all connected brokers for the user.

**Response (200):**
```json
[
  {
    "id": 1,
    "broker_name": "Zerodha",
    "is_active": true,
    "credentials": { ... }
  },
  {
    "id": 2,
    "broker_name": "Angel One",
    "is_active": true,
    "credentials": { ... }
  }
]
```

---

### DELETE /brokers/{broker_id}

Disconnect and remove a broker.

**Response (200):**
```json
{
  "message": "Broker deleted"
}
```

**Errors:**
- `404` - Broker not found

---

## Admin Endpoints

### GET /admin/users

List all registered users.

**Response (200):**
```json
[
  {
    "id": 1,
    "username": "trader123",
    "email": "trader@example.com",
    "role": "Trader",
    "is_active": true
  }
]
```

---

## WebSocket Endpoints

### WS /ws/market-data

Connect to real-time market data stream.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8001/api/ws/market-data');
```

**Incoming Message:**
```json
{
  "symbol": "NIFTY 50",
  "price": 22005.45,
  "timestamp": 1234567.89
}
```

**Frequency:** 1 message per second

---

## Health & Status

### GET /

API root endpoint.

**Response (200):**
```json
{
  "message": "Insight Engine V2 API is running"
}
```

---

## Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid input) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found |
| 422 | Validation error |
| 500 | Internal server error |

---

## Rate Limits (Planned)

| Endpoint | Limit |
|----------|-------|
| POST /auth/login | 5 per minute per IP |
| POST /auth/register | 3 per hour per IP |
| POST /auth/password-reset-request | 3 per hour per email |
| All other endpoints | 100 per minute per IP |

---

## Authentication Flow Example

```bash
# 1. Register
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"trader123","email":"trader@example.com","password":"SecurePass123!"}'

# 2. Login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"trader123","password":"SecurePass123!"}'

# Response: {"token": "eyJ...", "token_type": "bearer"}

# 3. Access protected endpoint
curl http://localhost:8001/api/brokers/ \
  -H "Authorization: Bearer eyJ..."
```
