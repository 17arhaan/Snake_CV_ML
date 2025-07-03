#!/usr/bin/env python3
"""
Enhanced backend for Snake CV with finger pointing detection
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import cv2
import numpy as np
import base64
import time
import json

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173", "http://127.0.0.1:5173"])

class FingerDetector:
    def __init__(self):
        self.prev_frame = None
        self.last_direction_time = 0
        self.direction_cooldown = 0.5  # seconds
        self.motion_threshold = 30
        
    def detect_finger_direction(self, frame):
        """Detect finger pointing direction using motion and contour detection"""
        h, w = frame.shape[:2]
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define skin color range (simplified)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create skin mask
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Apply some morphological operations to clean up the mask
        kernel = np.ones((5,5), np.uint8)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
            
        # Find the largest contour (assuming it's the hand)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Check if contour is large enough
        if cv2.contourArea(largest_contour) < 1000:
            return None
            
        # Get the convex hull and find the tip (pointing finger)
        hull = cv2.convexHull(largest_contour, returnPoints=True)
        
        if len(hull) < 3:
            return None
            
        # Find the topmost point as potential finger tip
        finger_tip = tuple(hull[hull[:, :, 1].argmin()][0])
        
        # Get centroid of contour
        M = cv2.moments(largest_contour)
        if M["m00"] == 0:
            return None
            
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        # Calculate direction from centroid to finger tip
        dx = finger_tip[0] - cx
        dy = finger_tip[1] - cy
        
        # Define directional zones (expanded for better detection)
        center_x, center_y = w // 2, h // 2
        zone_size = min(w, h) * 0.3
        
        # Check if finger tip is in any of the directional zones
        current_time = time.time()
        if current_time - self.last_direction_time > self.direction_cooldown:
            
            # UP zone (top third of screen)
            if finger_tip[1] < center_y - zone_size * 0.5:
                self.last_direction_time = current_time
                return "UP"
            
            # DOWN zone (bottom third of screen) 
            elif finger_tip[1] > center_y + zone_size * 0.5:
                self.last_direction_time = current_time
                return "DOWN"
                
            # LEFT zone (left third of screen)
            elif finger_tip[0] < center_x - zone_size * 0.5:
                self.last_direction_time = current_time
                return "LEFT"
                
            # RIGHT zone (right third of screen)
            elif finger_tip[0] > center_x + zone_size * 0.5:
                self.last_direction_time = current_time
                return "RIGHT"
        
        return None
    
    def detect_motion_direction(self, frame):
        """Fallback motion detection"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.prev_frame is not None:
            # Calculate frame difference
            diff = cv2.absdiff(self.prev_frame, gray)
            _, thresh = cv2.threshold(diff, self.motion_threshold, 255, cv2.THRESH_BINARY)
            
            # Find contours of motion
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find largest motion area
                largest_motion = max(contours, key=cv2.contourArea)
                
                if cv2.contourArea(largest_motion) > 500:
                    # Get centroid of motion
                    M = cv2.moments(largest_motion)
                    if M["m00"] != 0:
                        motion_x = int(M["m10"] / M["m00"])
                        motion_y = int(M["m01"] / M["m00"])
                        
                        # Determine direction based on motion position
                        h, w = frame.shape[:2]
                        center_x, center_y = w // 2, h // 2
                        threshold = min(w, h) * 0.2
                        
                        current_time = time.time()
                        if current_time - self.last_direction_time > self.direction_cooldown:
                            if motion_x < center_x - threshold:
                                self.last_direction_time = current_time
                                return "LEFT"
                            elif motion_x > center_x + threshold:
                                self.last_direction_time = current_time
                                return "RIGHT"
                            elif motion_y < center_y - threshold:
                                self.last_direction_time = current_time
                                return "UP"
                            elif motion_y > center_y + threshold:
                                self.last_direction_time = current_time
                                return "DOWN"
        
        self.prev_frame = gray.copy()
        return None

# Global detector instance
detector = FingerDetector()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Enhanced Snake CV backend running",
        "timestamp": time.time(),
        "features": ["finger_detection", "motion_detection"],
        "port": 5001
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint"""
    return jsonify({
        "message": "Enhanced backend working!",
        "timestamp": time.time(),
        "version": "2.0"
    })

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Process a frame for finger/motion detection"""
    try:
        data = request.get_json()
        
        if 'frame' not in data:
            return jsonify({"error": "No frame data provided"}), 400
        
        # Decode base64 image
        frame_data = data['frame'].split(',')[1]
        frame_bytes = base64.b64decode(frame_data)
        
        # Convert to OpenCV format
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Invalid frame data"}), 400
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect finger direction (primary method)
        direction = detector.detect_finger_direction(frame)
        
        # Fallback to motion detection if no finger detected
        if not direction:
            direction = detector.detect_motion_direction(frame)
        
        # Prepare response
        response = {
            "direction": direction,
            "gesture": direction,  # For compatibility
            "blink": False,
            "calibrated": True,
            "timestamp": time.time()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error processing frame: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/set_sensitivity', methods=['POST'])
def set_sensitivity():
    """Adjust detection sensitivity"""
    try:
        data = request.get_json()
        sensitivity = data.get('sensitivity', 30)
        
        # Convert percentage to threshold (inverted - higher sensitivity = lower threshold)
        detector.motion_threshold = max(10, min(100, 110 - sensitivity))
        
        return jsonify({
            "message": "Sensitivity updated",
            "sensitivity": sensitivity,
            "threshold": detector.motion_threshold
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/set_detection_mode', methods=['POST'])
def set_detection_mode():
    """Set detection mode"""
    try:
        data = request.get_json()
        mode = data.get('mode', 'motion')
        
        return jsonify({
            "message": f"Detection mode set to {mode}",
            "mode": mode,
            "note": "Using combined finger + motion detection"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'message': 'Connected to Enhanced Snake CV backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('frame_data')
def handle_frame_data(data):
    """Handle real-time frame processing via WebSocket"""
    try:
        # Decode and process frame
        frame_data = data['frame'].split(',')[1]
        frame_bytes = base64.b64decode(frame_data)
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is not None:
            frame = cv2.flip(frame, 1)
            
            # Detect finger direction (primary)
            direction = detector.detect_finger_direction(frame)
            
            # Fallback to motion detection
            if not direction:
                direction = detector.detect_motion_direction(frame)
            
            # Send result back to client
            if direction:
                emit('detection_result', {
                    'direction': direction,
                    'gesture': direction,
                    'blink': False,
                    'calibrated': True,
                    'timestamp': time.time()
                })
                
    except Exception as e:
        print(f"WebSocket frame processing error: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    print("🚀 Enhanced Snake CV Backend")
    print("🌐 Available at: http://localhost:5001")
    print("🔧 Health check: http://localhost:5001/health")
    print("👆 Features: Finger pointing + Motion detection")
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True) 