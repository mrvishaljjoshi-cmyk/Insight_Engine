#!/bin/bash
# Deployment script for Insight
# Usage: ./deploy.sh [production|development]

set -e

ENV=${1:-production}
echo "Deploying Insight in $ENV mode..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

print_info() {
    echo -e "${YELLOW}INFO: $1${NC}"
}

# Check if running as root for production
if [ "$ENV" = "production" ] && [ "$EUID" -ne 0 ]; then
    print_error "Production deployment requires root privileges"
    exit 1
fi

# Setup directories
PROJECT_DIR="/home/VJPROJECTS/Insight_Engine"
WEB_ROOT="/home/VJPROJECTS/Insight_Engine/frontend_native"

print_info "Using project directory for live site..."
# No need to copy files anymore

# Setup Backend
print_info "Setting up backend..."
cd $PROJECT_DIR/backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -q --upgrade pip
pip install -q -r requirements.txt
print_success "Backend dependencies installed"

# Setup systemd service for production
if [ "$ENV" = "production" ]; then
    print_info "Setting up systemd service..."

    cat > /etc/systemd/system/insight-backend.service << EOF
[Unit]
Description=Insight Backend API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR/backend
Environment="PATH=$PROJECT_DIR/backend/venv/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=$PROJECT_DIR/backend/.env
ExecStart=$PROJECT_DIR/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    systemctl daemon-reload
    systemctl enable insight-backend
    print_success "Systemd service configured"

    # Setup Nginx
    print_info "Configuring Nginx..."
    cp $PROJECT_DIR/nginx.conf /etc/nginx/sites-available/insight

    # Enable site
    if [ ! -L "/etc/nginx/sites-enabled/insight" ]; then
        ln -s /etc/nginx/sites-available/insight /etc/nginx/sites-enabled/
    fi

    # Test Nginx config
    nginx -t
    systemctl reload nginx
    print_success "Nginx configured"

    # Start/Restart service
    print_info "Starting Insight backend..."
    systemctl restart insight-backend
    print_success "Insight backend started"

else
    # Development mode
    print_info "Starting in development mode..."
    cd $PROJECT_DIR/backend
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &

    cd $PROJECT_DIR/frontend_native
    python3 -m http.server 8081 &

    print_success "Development servers started on ports 8001 (API) and 8081 (Frontend)"
fi

# Health check
print_info "Running health check..."
sleep 2
curl -s http://localhost:8001/health || print_error "Health check failed"

print_success "Deployment complete!"
print_info "Your application is available at:"
if [ "$ENV" = "production" ]; then
    echo "  https://insight.vjprojects.co.in"
else
    echo "  Frontend: http://localhost:8081"
    echo "  API:      http://localhost:8001"
fi
