#!/bin/bash
# Bare Metal Setup for Insight Engine Pure Native Build

echo "🚀 Starting Bare Metal Setup..."

# 1. Update & Install System Dependencies
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip nginx redis-server

# 2. Setup Backend Virtual Environment
echo "📦 Setting up Python Venv..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# 3. Configure Nginx
echo "⚙️ Configuring Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/insight-engine
sudo ln -s /etc/nginx/sites-available/insight-engine /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# 4. Create Systemd Service for FastAPI
echo "🛠️ Creating Systemd Service..."
cat << SERVICE | sudo tee /etc/systemd/system/insight-backend.service
[Unit]
Description=Insight Engine FastAPI Backend
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)/backend
Environment="PATH=$(pwd)/backend/venv/bin"
ExecStart=$(pwd)/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable insight-backend
sudo systemctl restart insight-backend

echo "✅ Setup Complete! Access UI at http://insight.vjprojects.co.in"
