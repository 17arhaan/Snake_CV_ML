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
   pip install opencv-python flask flask-cors numpy websockets python-socketio flask-socketio eventlet
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
   - Backend API: http://localhost:5000

## 🎮 How to Play

### Game Controls
- **Arrow Keys**: Use arrow keys to control the snake
- **Spacebar**: Pause/Resume game
- **Mouse**: Click buttons for menu navigation

### Computer Vision Controls
- **Motion Detection**: Move your body to control the snake (works without MediaPipe)
- **Gesture Detection**: Point with your finger in the direction you want to move (requires MediaPipe)
- **Head Movement**: Move your head to control the snake (requires MediaPipe)

## 🛠️ Features

### Core Game Features
- Classic Snake gameplay with modern graphics
- Score tracking and high score persistence
- Smooth animations and death effects
- Replay system with playback controls
- Responsive design

### Computer Vision Features
- **Motion Detection**: Uses optical flow to detect body movement
- **Hand Gesture Recognition**: Detect pointing gestures for direction control
- **Head Movement Tracking**: Track head position for hands-free control
- **Real-time Processing**: WebSocket communication for low-latency control

## 🔧 Troubleshooting

### Backend Issues
- **MediaPipe Not Available**: The game will work with motion detection only
- **Camera Not Detected**: Check camera permissions and availability
- **Port 5000 Already in Use**: Stop other services using port 5000

### Frontend Issues
- **Dependencies Not Installing**: Try `npm install --force`
- **Port 5173 Already in Use**: Vite will automatically use the next available port

### Common Solutions
1. **Check if backend is running**:
   ```bash
   curl http://localhost:5000/health
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
├── backend/          # Python Flask backend
│   ├── app.py       # Main backend application
│   ├── start_backend.py  # Backend startup script
│   └── venv/        # Python virtual environment
├── src/             # React frontend
│   ├── components/  # React components
│   ├── hooks/       # Custom React hooks
│   └── main.tsx     # Frontend entry point
├── package.json     # Frontend dependencies
└── requirements.txt # Python dependencies
```

## 🎯 Game Modes

### Detection Modes
1. **Motion Detection**: Detects body movement using optical flow
2. **Gesture Detection**: Recognizes hand gestures (requires MediaPipe)
3. **Head Tracking**: Tracks head movement (requires MediaPipe)

### Control Sensitivity
- Adjustable sensitivity slider in the OpenCV controls
- Cooldown periods to prevent rapid direction changes

## 🔍 Technical Details

### Frontend Stack
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Socket.IO** for real-time communication

### Backend Stack
- **Flask** web framework
- **OpenCV** for computer vision
- **MediaPipe** for gesture recognition (optional)
- **Socket.IO** for WebSocket communication
- **NumPy** for numerical operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🎮 Enjoy the Game!

Have fun playing Snake with computer vision controls! 🐍✨