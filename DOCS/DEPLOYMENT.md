# Insight Engine - Deployment Guide

**Version:** 2.0  
**Last Updated:** 2026-04-20

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Native Deployment (Recommended)](#native-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 2 GB | 4 GB |
| Storage | 10 GB | 20 GB SSD |
| OS | Ubuntu 20.04+ | Ubuntu 22.04 LTS |

### Required Software

```bash
# Python 3.10+
python3 --version

# pip
pip3 --version

# Nginx
nginx -v

# PostgreSQL (optional for native, required for Docker)
psql --version

# Docker & Docker Compose (for Docker deployment)
docker --version
docker-compose --version
```

---

## Native Deployment (Recommended)

### Step 1: System Preparation

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3-venv python3-pip nginx redis-server
```

### Step 2: Clone/Setup Project

```bash
cd /home/VJPROJECTS/Insight_Engine

# Make setup script executable
chmod +x setup.sh
```

### Step 3: Configure Environment

```bash
# Create backend .env file
cat > backend/.env << EOF
SECRET_KEY=your_secure_secret_key_here
DATABASE_URL=postgresql://insight_user:insight_pass@localhost/insight_db
GOOGLE_CLIENT_ID=your_google_client_id
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
```

### Step 4: Run Setup Script

```bash
./setup.sh
```

This script will:
1. Create Python virtual environment
2. Install dependencies
3. Configure Nginx
4. Create systemd service for backend
5. Start all services

### Step 5: Verify Deployment

```bash
# Check backend status
sudo systemctl status insight-backend

# Check Nginx status
sudo systemctl status nginx

# Test backend
curl http://localhost:8001/api/

# Test frontend
curl http://localhost:8081/
```

### Step 6: Configure Domain (Optional)

```bash
# Update Nginx server_name
sudo nano /etc/nginx/sites-available/insight-engine

# Change:
# server_name localhost;
# To:
# server_name insight.vjprojects.co.in;

# Reload Nginx
sudo nginx -t && sudo systemctl reload nginx
```

---

## Docker Deployment

### Step 1: Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Configure Environment

```bash
cd /home/VJPROJECTS/Insight_Engine

# Create .env file
cat > .env << EOF
SECRET_KEY=your_secure_secret_key_here
DATABASE_URL=postgresql://insight_user:insight_pass@db/insight_db
GOOGLE_CLIENT_ID=your_google_client_id
VITE_GOOGLE_CLIENT_ID=your_google_client_id
EOF
```

### Step 3: Build and Start

```bash
# Build all containers
docker-compose build

# Start services
docker-compose up -d
```

### Step 4: Verify

```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs -f backend

# Test API
curl http://localhost:8001/api/
```

### Step 5: Initialize Database

```bash
# Run database initialization
docker-compose exec backend python init_db.py
```

---

## Configuration

### Nginx Configuration

Location: `/etc/nginx/sites-available/insight-engine`

```nginx
server {
    listen 80;
    server_name insight.vjprojects.co.in;

    # Frontend
    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /api/ws/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Systemd Service

Location: `/etc/systemd/system/insight-backend.service`

```ini
[Unit]
Description=Insight Engine FastAPI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Insight_Engine/backend
Environment="PATH=/home/ubuntu/Insight_Engine/backend/venv/bin"
ExecStart=/home/ubuntu/Insight_Engine/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| SECRET_KEY | JWT signing key | (none) | Yes |
| DATABASE_URL | Database connection | sqlite:///./insight_engine.db | No |
| GOOGLE_CLIENT_ID | OAuth client ID | (none) | No |
| REDIS_HOST | Redis server | localhost | No |
| REDIS_PORT | Redis port | 6379 | No |

---

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
sudo journalctl -u insight-backend -n 50

# Common issues:
# 1. Port already in use
sudo lsof -i :8001

# 2. Missing dependencies
cd backend && source venv/bin/activate && pip install -r requirements.txt

# 3. Database connection failed
# Check DATABASE_URL in .env
```

### Nginx Errors

```bash
# Test configuration
sudo nginx -t

# Check error log
sudo tail -f /var/log/nginx/error.log

# Reload after changes
sudo systemctl reload nginx
```

### Database Issues

```bash
# For PostgreSQL
sudo -u postgres psql -c "SELECT 1"

# Check if database exists
sudo -u postgres psql -l | grep insight_db

# Create if missing
sudo -u postgres createdb insight_db
sudo -u postgres psql -c "CREATE USER insight_user WITH PASSWORD 'insight_pass';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE insight_db TO insight_user;"
```

### WebSocket Not Connecting

```bash
# Check if backend is running
curl http://localhost:8001/api/

# Check Nginx WebSocket config
# Ensure proxy_set_header Upgrade and Connection are set

# Test direct WebSocket connection
wscat -c ws://localhost:8001/api/ws/market-data
```

### SSL/Cloudflare Setup

1. Create Cloudflare account
2. Add domain: insight.vjprojects.co.in
3. Change nameservers to Cloudflare
4. Enable SSL/TLS: Full mode
5. Create A record: insight -> your_server_ip
6. Origin Certificate: Install in Nginx

```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cloudflare-origin.pem;
    ssl_certificate_key /path/to/cloudflare-origin.key;
    ...
}
```

---

## Monitoring

### Service Health

```bash
# Backend
sudo systemctl status insight-backend

# Nginx
sudo systemctl status nginx

# PostgreSQL (if used)
sudo systemctl status postgresql

# Redis
sudo systemctl status redis-server
```

### Logs

```bash
# Backend logs
sudo journalctl -u insight-backend -f

# Nginx access log
sudo tail -f /var/log/nginx/access.log

# Nginx error log
sudo tail -f /var/log/nginx/error.log
```

### Performance

```bash
# CPU/Memory
htop

# Disk usage
df -h

# Network connections
netstat -tulpn | grep -E '8001|8081'
```

---

## Backup & Restore

### Database Backup (SQLite)

```bash
# Backup
cp /path/to/insight_engine.db /path/to/backup_$(date +%Y%m%d).db

# Restore
cp /path/to/backup_20260420.db /path/to/insight_engine.db
```

### Database Backup (PostgreSQL)

```bash
# Backup
pg_dump -U insight_user insight_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U insight_user insight_db < backup_20260420.sql
```

---

## Update Procedure

```bash
cd /home/VJPROJECTS/Insight_Engine

# Pull latest changes (if using git)
git pull origin main

# Update dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart backend
sudo systemctl restart insight-backend

# Verify
curl http://localhost:8001/api/
```
