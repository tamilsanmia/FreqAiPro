#!/bin/bash

# FreqAiPro - Full Stack Setup Script
# Sets up both Flask backend and Next.js frontend

set -e  # Exit on error

echo "================================"
echo "FreqAiPro Setup Script"
echo "================================"
echo ""

# Check if running from correct directory
if [ ! -f "app.py" ]; then
    echo "Error: Please run this script from the FreqAiPro directory"
    exit 1
fi

# Backend Setup
echo "[1/4] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "[2/4] Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Python dependencies installed"

# Frontend Setup
echo ""
echo "[3/4] Setting up Next.js frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    echo "✓ Node.js dependencies installed"
else
    echo "✓ Node.js dependencies already installed"
fi

# Create .env.local if doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:5000" > .env.local
    echo "✓ Environment file created"
else
    echo "✓ Environment file already exists"
fi

cd ..

# Check Redis
echo ""
echo "[4/4] Checking Redis..."
if systemctl is-active --quiet redis-server 2>/dev/null || pgrep redis-server >/dev/null 2>&1; then
    echo "✓ Redis is running"
else
    echo "⚠ Redis is not running (optional but recommended)"
    echo "  To install Redis:"
    echo "    sudo apt update && sudo apt install redis-server"
    echo "    sudo systemctl start redis-server"
fi

echo ""
echo "================================"
echo "Setup Complete! 🎉"
echo "================================"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd $(pwd)"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd $(pwd)/frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
