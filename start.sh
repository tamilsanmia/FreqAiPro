#!/bin/bash

# FreqAiPro - Quick Start Script
# Runs both backend and frontend in parallel

echo "🚀 Starting FreqAiPro..."
echo ""

# Check if setup has been run
if [ ! -d "venv" ] || [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  First-time setup required!"
    echo "Running setup.sh..."
    ./setup.sh
    echo ""
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "📡 Starting Flask backend..."
cd "$(dirname "$0")"
source venv/bin/activate
python app.py &
BACKEND_PID=$!
echo "✓ Backend running (PID: $BACKEND_PID) on http://localhost:5000"

# Wait for backend to start
sleep 3

# Start frontend
echo "🌐 Starting Next.js frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "✓ Frontend running (PID: $FRONTEND_PID) on http://localhost:3000"

echo ""
echo "================================"
echo "✅ FreqAiPro is running!"
echo "================================"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for processes
wait
