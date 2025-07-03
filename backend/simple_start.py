#!/usr/bin/env python3
"""
Simple backend starter for Snake CV
"""

import sys
import os
import time

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🐍 Starting Snake CV Backend")
    print("=" * 40)
    
    # Try to import required modules
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    # Try to import MediaPipe (optional)
    try:
        import mediapipe as mp
        print("✅ MediaPipe imported successfully")
    except ImportError:
        print("⚠️  MediaPipe not available (gesture detection disabled)")
    
    print("\n🚀 Starting Flask server...")
    print("🌐 Backend will be available at: http://localhost:5000")
    print("📡 WebSocket endpoint: ws://localhost:5000/socket.io")
    print("🔧 Health check: http://localhost:5000/health")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        # Import and run the Flask app
        from app import socketio, app
        
        # Start the server
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5000, 
            debug=True,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 