#!/usr/bin/env python3
"""
Snake Game OpenCV Backend Starter
Handles computer vision processing for the Snake game
"""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'opencv-python',
        'flask',
        'flask-cors',
        'numpy',
        'mediapipe',
        'websockets',
        'python-socketio',
        'flask-socketio',
        'eventlet'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                *missing_packages
            ])
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            return False
    
    return True

def check_camera():
    """Check if camera is available"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("✅ Camera is available and working")
                return True
            else:
                print("⚠️  Camera detected but unable to read frames")
                return False
        else:
            print("❌ No camera detected")
            return False
    except Exception as e:
        print(f"❌ Camera check failed: {e}")
        return False

def start_backend():
    """Start the Flask backend server"""
    try:
        print("🚀 Starting OpenCV Snake Game Backend...")
        print("📡 Server will be available at: http://localhost:5000")
        print("🎮 WebSocket endpoint: ws://localhost:5000/socket.io")
        print("\n📋 Available endpoints:")
        print("   GET  /health - Health check")
        print("   POST /process_frame - Process single frame")
        print("   POST /set_sensitivity - Adjust sensitivity")
        print("   POST /set_detection_mode - Set detection mode")
        print("\n🎯 Detection modes:")
        print("   - motion: Optical flow motion detection")
        print("   - gesture: Hand gesture recognition")
        print("   - head: Head movement tracking")
        print("\n" + "="*50)
        
        # Import and run the Flask app
        from app import socketio, app
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False
    
    return True

def test_backend():
    """Test if backend is running correctly"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy!")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def main():
    """Main function to start the backend"""
    print("🐍 Snake Game OpenCV Backend")
    print("="*40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        sys.exit(1)
    
    print("✅ All dependencies are installed")
    
    # Check camera
    camera_available = check_camera()
    if not camera_available:
        print("⚠️  Camera not available - some features may not work")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Start backend
    print("\n🚀 Starting backend server...")
    start_backend()

if __name__ == "__main__":
    main()