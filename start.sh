#!/bin/bash

# Snake CV - Computer Vision Snake Game Startup Script
# This script starts both the frontend and backend services

echo "🐍 Starting Snake CV - Computer Vision Snake Game"
echo "=================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Create virtual environment and install backend dependencies if needed
if [ ! -d "backend/venv" ]; then
    echo "📦 Setting up Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install opencv-python flask flask-cors numpy websockets python-socketio flask-socketio eventlet
    cd ..
fi

echo "🚀 Starting services..."

# Start backend in the background
echo "🐍 Starting Python backend..."
cd backend
source venv/bin/activate
python start_backend.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in the background
echo "⚛️  Starting React frontend..."
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

echo ""
echo "✅ Services started successfully!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait 