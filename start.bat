@echo off
REM Snake CV - Computer Vision Snake Game Startup Script (Windows)
REM This script starts both the frontend and backend services

echo 🐍 Starting Snake CV - Computer Vision Snake Game
echo ==================================================

REM Check if Node.js is installed
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python first.
    pause
    exit /b 1
)

REM Install frontend dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing frontend dependencies...
    npm install
)

REM Create virtual environment and install backend dependencies if needed
if not exist "backend\venv" (
    echo 📦 Setting up Python virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install opencv-python flask flask-cors numpy websockets python-socketio flask-socketio eventlet
    cd ..
)

echo 🚀 Starting services...

REM Start backend in the background
echo 🐍 Starting Python backend...
cd backend
call venv\Scripts\activate
start /b python start_backend.py
cd ..

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo ⚛️  Starting React frontend...
start /b npm run dev

REM Wait a moment for frontend to start
timeout /t 3 /nobreak >nul

echo.
echo ✅ Services started successfully!
echo 🌐 Frontend: http://localhost:5173
echo 🔧 Backend API: http://localhost:5000
echo.
echo Press any key to stop all services...
pause >nul

REM Cleanup
echo 🛑 Stopping services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo ✅ Services stopped 