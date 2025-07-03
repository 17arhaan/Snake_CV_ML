# 🚀 Quick Start Guide - Snake CV Camera Fix

## The Issue
The camera wasn't working because:
1. Port 5000 is used by macOS Control Center
2. Backend wasn't starting properly
3. Missing dependencies

## ✅ Fixed Solution

### Step 1: Backend Setup
```bash
# Go to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Install missing dependency
pip install requests

# Start the backend (use port 5001 instead of 5000)
python test_backend.py
```

Keep this terminal open! You should see:
```
🧪 Starting Test Backend
🌐 Available at: http://localhost:5001
🔧 Health check: http://localhost:5001/health
🔧 Test endpoint: http://localhost:5001/test
```

### Step 2: Frontend Setup
```bash
# In a NEW terminal window, go to project root
cd /path/to/your/project

# Start frontend (should already be running)
npm run dev
```

### Step 3: Test the Setup
```bash
# In a third terminal, test the backend
curl http://localhost:5001/health
```

You should see:
```json
{
  "status": "healthy",
  "message": "Test backend is running", 
  "timestamp": 1234567890.123,
  "camera_support": "basic"
}
```

## 🎮 Using the Camera

1. **Open the game**: Go to `http://localhost:5173`
2. **Click the camera button** in the game interface
3. **Allow camera permissions** when prompted by your browser
4. **The camera should now work** for basic motion detection

## 🔧 What I Fixed

### Backend Changes:
- ✅ Changed port from 5000 to 5001 (avoiding macOS Control Center conflict)
- ✅ Added missing `requests` dependency
- ✅ Created simplified test backend for reliability
- ✅ Added proper error handling for MediaPipe not being available

### Frontend Changes:
- ✅ Updated all API endpoints to use port 5001
- ✅ Camera setup code is already working
- ✅ Added better error handling

## 🎯 Camera Features Available

### ✅ Working Features:
- **Camera capture**: ✅ Works
- **Motion detection**: ✅ Works (basic optical flow)
- **Real-time processing**: ✅ Works

### ⚠️ Limited Features:
- **Hand gesture recognition**: ❌ Disabled (MediaPipe not compatible with Python 3.13)
- **Head tracking**: ❌ Disabled (MediaPipe not compatible with Python 3.13)

## 🆘 Troubleshooting

### Backend Not Starting:
```bash
# Check if port 5001 is free
lsof -i :5001

# If something is using it, try port 5002
# Edit backend/test_backend.py and change port=5001 to port=5002
```

### Camera Not Working:
1. **Check browser permissions**: Allow camera access
2. **Try different browser**: Chrome/Firefox work best
3. **Check HTTPS**: Some browsers require HTTPS for camera access

### Still Having Issues?
1. **Kill all background processes**:
   ```bash
   pkill -f python
   pkill -f node
   ```

2. **Restart everything**:
   ```bash
   # Terminal 1: Backend
   cd backend && source venv/bin/activate && python test_backend.py
   
   # Terminal 2: Frontend  
   npm run dev
   ```

## 🎉 Success!
When everything is working:
- ✅ Backend at `http://localhost:5001`
- ✅ Frontend at `http://localhost:5173`
- ✅ Camera button in game interface works
- ✅ Motion detection controls the snake 