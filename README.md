# 🐍 Snake CV - Computer Vision Snake Game

A modern Snake game controlled by computer vision using OpenCV and MediaPipe, with a React frontend and Python backend.

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+ (Note: MediaPipe doesn't support Python 3.13 yet)

### Installation

1. **Install Frontend Dependencies**
   ```bash
   npm install
   ```

2. **Install Backend Dependencies**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install opencv-python flask flask-cors numpy websockets python-socketio flask-socketio eventlet requests
   ```

   *Note: MediaPipe is not available for Python 3.13 yet, so gesture and head detection are disabled.*

### Running the Game

1. **Start the Backend** (in terminal 1):
   ```bash
   cd backend
   source venv/bin/activate
   python start_backend.py
   ```

2. **Start the Frontend** (in terminal 2):
   ```bash
   npm run dev
   ```

3. **Open in Browser**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5001

## 🎮 How to Play

### Game Controls
- **Arrow Keys**: Use arrow keys or WASD to control the snake
- **Spacebar**: Pause/Resume game
- **Mouse**: Click buttons for menu navigation

### Computer Vision Controls
- **Motion Detection**: Move your body to control the snake (works without MediaPipe)
- **Finger Pointing**: Point with your finger in the direction you want to move
- **Head Movement**: Move your head to control the snake (requires MediaPipe)

## 🛠️ Features

### Core Game Features
- Classic Snake gameplay with modern retro graphics
- Score tracking and high score persistence
- Smooth animations and death effects with particle explosions
- Replay system with playback controls and speed adjustment
- Responsive design with mobile support
- Multiple game states (menu, playing, paused, game over, replay)

### Computer Vision Features
- **Motion Detection**: Uses optical flow to detect body movement
- **Finger Pointing Detection**: Detect pointing gestures using skin color detection
- **Hand Gesture Recognition**: Detect pointing gestures for direction control
- **Head Movement Tracking**: Track head position for hands-free control
- **Real-time Processing**: WebSocket communication for low-latency control
- **Camera Preview**: Live camera feed in the UI

### Technical Features
- **React Frontend**: Modern TypeScript React app with Tailwind CSS
- **Python Backend**: Flask server with OpenCV and computer vision processing
- **WebSocket Communication**: Real-time bidirectional communication
- **Modular Architecture**: Clean separation of concerns

## 🔧 Troubleshooting

### Backend Issues
- **MediaPipe Not Available**: The game will work with motion detection only
- **Camera Not Detected**: Check camera permissions and availability
- **Port 5001 Already in Use**: Stop other services using port 5001 (changed from 5000 for macOS compatibility)

### Frontend Issues
- **Dependencies Not Installing**: Try `npm install --force`
- **Port 5173 Already in Use**: Vite will automatically use the next available port

### Common Solutions
1. **Check if backend is running**:
   ```bash
   curl http://localhost:5001/health
   ```

2. **Restart backend with debug**:
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

3. **Check camera permissions** in your browser settings

## 📦 Project Structure

```
snake-cv/
├── backend/                    # Python Flask backend
│   ├── app.py                 # Main backend application
│   ├── enhanced_backend.py    # Enhanced backend with finger detection
│   ├── start_backend.py       # Backend startup script
│   └── computer_vision.py     # Computer vision processing
├── src/                       # React frontend
│   ├── components/            # React components
│   │   ├── SnakeGame.tsx     # Main game component
│   │   └── OpenCVControls.tsx # Computer vision controls
│   ├── hooks/                 # Custom React hooks
│   │   └── useOpenCVBackend.ts # Backend integration hook
│   └── main.tsx               # Frontend entry point
├── package.json               # Frontend dependencies
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🎯 Game Modes

### Detection Modes
1. **Motion Detection**: Detects body movement using optical flow
2. **Finger Pointing**: Recognizes pointing gestures using skin color detection
3. **Gesture Detection**: Recognizes hand gestures (requires MediaPipe)
4. **Head Tracking**: Tracks head movement (requires MediaPipe)

### Control Sensitivity
- Adjustable sensitivity slider in the OpenCV controls
- Cooldown periods to prevent rapid direction changes
- Directional zones for accurate control

## 🔍 Technical Details

### Frontend Stack
- **React 18** with TypeScript
- **Vite** for fast development and hot reload
- **Tailwind CSS** for styling and responsive design
- **Socket.IO** for real-time communication
- **Lucide React** for icons

### Backend Stack
- **Flask** web framework
- **OpenCV** for computer vision processing
- **MediaPipe** for gesture recognition (optional)
- **Socket.IO** for WebSocket communication
- **NumPy** for numerical operations
- **Requests** for HTTP handling

### Computer Vision Processing
- **Skin Color Detection**: HSV color space filtering
- **Contour Analysis**: Finding hand and finger tip
- **Optical Flow**: Motion detection for body movement
- **Real-time Processing**: Frame-by-frame analysis

## 🚀 Deployment

### Development Mode
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python start_backend.py

# Terminal 2: Frontend
npm run dev
```

### Production Build
```bash
# Build frontend
npm run build

# Serve frontend (optional)
npm run preview
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🎮 Enjoy the Game!

Have fun playing Snake with computer vision controls! 🐍✨

---

*Created with ❤️ using React, Python, OpenCV, and modern web technologies.*
