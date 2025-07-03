import cv2
import numpy as np
# Try to import mediapipe, but handle gracefully if not available
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️  MediaPipe not available. Hand gesture and head movement detection will be disabled.")

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import base64
import json
import threading
import time
from collections import deque
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'snake_game_secret'
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173", "http://127.0.0.1:5173"])

class MotionDetector:
    def __init__(self):
        if MEDIAPIPE_AVAILABLE:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
        else:
            self.hands = None
            self.pose = None
        
        # Motion detection parameters
        self.prev_frame = None
        self.motion_threshold = 25
        self.direction_history = deque(maxlen=5)
        self.last_direction_time = 0
        self.direction_cooldown = 0.8  # seconds
        
        # Gesture detection
        self.gesture_history = deque(maxlen=10)
        self.last_gesture_time = 0
        
    def detect_hand_gesture(self, frame):
        """Detect hand gestures for game control"""
        if not MEDIAPIPE_AVAILABLE or not self.hands:
            return None
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get hand landmarks
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append([lm.x, lm.y])
                
                # Detect gestures based on hand position and orientation
                gesture = self._classify_hand_gesture(landmarks)
                if gesture:
                    return gesture
        
        return None
    
    def _classify_hand_gesture(self, landmarks):
        """Classify hand gesture based on landmarks"""
        if len(landmarks) < 21:
            return None
            
        # Get key points
        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Calculate relative positions
        thumb_up = thumb_tip[1] < wrist[1] - 0.1
        index_up = index_tip[1] < wrist[1] - 0.1
        middle_up = middle_tip[1] < wrist[1] - 0.1
        ring_up = ring_tip[1] < wrist[1] - 0.1
        pinky_up = pinky_tip[1] < wrist[1] - 0.1
        
        # Gesture recognition
        if index_up and not middle_up and not ring_up and not pinky_up:
            # Pointing gesture - determine direction
            if index_tip[0] < wrist[0] - 0.15:
                return "LEFT"
            elif index_tip[0] > wrist[0] + 0.15:
                return "RIGHT"
            elif index_tip[1] < wrist[1] - 0.15:
                return "UP"
            elif index_tip[1] > wrist[1] + 0.1:
                return "DOWN"
        
        elif thumb_up and index_up and not middle_up and not ring_up and not pinky_up:
            return "PAUSE"
        
        elif thumb_up and index_up and middle_up and ring_up and pinky_up:
            return "RESET"
            
        return None
    
    def detect_head_movement(self, frame):
        """Detect head movement for direction control"""
        if not MEDIAPIPE_AVAILABLE or not self.pose:
            return None
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            # Get nose landmark for head tracking
            nose = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            
            # Convert to pixel coordinates
            h, w = frame.shape[:2]
            nose_x = int(nose.x * w)
            nose_y = int(nose.y * h)
            
            # Determine direction based on nose position
            center_x, center_y = w // 2, h // 2
            threshold = min(w, h) * 0.15
            
            current_time = time.time()
            if current_time - self.last_direction_time > self.direction_cooldown:
                if nose_x < center_x - threshold:
                    self.last_direction_time = current_time
                    return "LEFT"
                elif nose_x > center_x + threshold:
                    self.last_direction_time = current_time
                    return "RIGHT"
                elif nose_y < center_y - threshold:
                    self.last_direction_time = current_time
                    return "UP"
                elif nose_y > center_y + threshold:
                    self.last_direction_time = current_time
                    return "DOWN"
        
        return None
    
    def detect_motion_direction(self, frame):
        """Detect motion direction using optical flow"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.prev_frame is not None:
            # Calculate optical flow
            flow = cv2.calcOpticalFlowPyrLK(
                self.prev_frame, gray, None, None,
                winSize=(15, 15),
                maxLevel=2,
                criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
            )
            
            # Analyze motion vectors
            h, w = frame.shape[:2]
            center_x, center_y = w // 2, h // 2
            
            # Create grid of points to track
            points = []
            for y in range(center_y - 50, center_y + 50, 10):
                for x in range(center_x - 50, center_x + 50, 10):
                    if 0 <= x < w and 0 <= y < h:
                        points.append([[x, y]])
            
            if points:
                points = np.array(points, dtype=np.float32)
                next_points, status, error = cv2.calcOpticalFlowPyrLK(
                    self.prev_frame, gray, points, None
                )
                
                # Calculate average motion
                good_points = next_points[status == 1]
                good_old = points[status == 1]
                
                if len(good_points) > 5:
                    motion_x = np.mean(good_points[:, 0] - good_old[:, 0])
                    motion_y = np.mean(good_points[:, 1] - good_old[:, 1])
                    
                    # Determine direction
                    threshold = 2.0
                    current_time = time.time()
                    
                    if current_time - self.last_direction_time > self.direction_cooldown:
                        if abs(motion_x) > abs(motion_y):
                            if motion_x > threshold:
                                self.last_direction_time = current_time
                                return "RIGHT"
                            elif motion_x < -threshold:
                                self.last_direction_time = current_time
                                return "LEFT"
                        else:
                            if motion_y > threshold:
                                self.last_direction_time = current_time
                                return "DOWN"
                            elif motion_y < -threshold:
                                self.last_direction_time = current_time
                                return "UP"
        
        self.prev_frame = gray.copy()
        return None

# Global motion detector instance
motion_detector = MotionDetector()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "OpenCV backend is running",
        "mediapipe_available": MEDIAPIPE_AVAILABLE,
        "supported_modes": ["motion"] + (["gesture", "head"] if MEDIAPIPE_AVAILABLE else [])
    })

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Process a single frame for motion/gesture detection"""
    try:
        data = request.get_json()
        
        if 'frame' not in data:
            return jsonify({"error": "No frame data provided"}), 400
        
        # Decode base64 image
        frame_data = data['frame'].split(',')[1]  # Remove data:image/jpeg;base64,
        frame_bytes = base64.b64decode(frame_data)
        
        # Convert to OpenCV format
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Invalid frame data"}), 400
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect gestures and motion
        detection_mode = data.get('mode', 'motion')  # 'motion', 'gesture', 'head'
        
        direction = None
        gesture = None
        
        if detection_mode == 'gesture':
            if not MEDIAPIPE_AVAILABLE:
                return jsonify({"error": "MediaPipe not available. Hand gesture detection is disabled."}), 400
            gesture = motion_detector.detect_hand_gesture(frame)
            if gesture in ['LEFT', 'RIGHT', 'UP', 'DOWN']:
                direction = gesture
        elif detection_mode == 'head':
            if not MEDIAPIPE_AVAILABLE:
                return jsonify({"error": "MediaPipe not available. Head movement detection is disabled."}), 400
            direction = motion_detector.detect_head_movement(frame)
        else:  # motion detection
            direction = motion_detector.detect_motion_direction(frame)
        
        # Prepare response
        response = {
            "direction": direction,
            "gesture": gesture,
            "timestamp": time.time()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing frame: {str(e)}")
        return jsonify({"error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connected', {'message': 'Connected to OpenCV backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

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
            
            detection_mode = data.get('mode', 'motion')
            direction = None
            gesture = None
            
            if detection_mode == 'gesture':
                if not MEDIAPIPE_AVAILABLE:
                    emit('error', {'message': 'MediaPipe not available. Hand gesture detection is disabled.'})
                    return
                gesture = motion_detector.detect_hand_gesture(frame)
                if gesture in ['LEFT', 'RIGHT', 'UP', 'DOWN']:
                    direction = gesture
            elif detection_mode == 'head':
                if not MEDIAPIPE_AVAILABLE:
                    emit('error', {'message': 'MediaPipe not available. Head movement detection is disabled.'})
                    return
                direction = motion_detector.detect_head_movement(frame)
            else:
                direction = motion_detector.detect_motion_direction(frame)
            
            # Send result back to client
            if direction or gesture:
                emit('detection_result', {
                    'direction': direction,
                    'gesture': gesture,
                    'timestamp': time.time()
                })
                
    except Exception as e:
        logger.error(f"WebSocket frame processing error: {str(e)}")
        emit('error', {'message': str(e)})

@app.route('/set_sensitivity', methods=['POST'])
def set_sensitivity():
    """Adjust motion detection sensitivity"""
    try:
        data = request.get_json()
        sensitivity = data.get('sensitivity', 25)
        
        motion_detector.motion_threshold = max(1, min(100, sensitivity))
        
        return jsonify({
            "message": "Sensitivity updated",
            "sensitivity": motion_detector.motion_threshold
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/set_detection_mode', methods=['POST'])
def set_detection_mode():
    """Set detection mode (motion, gesture, head)"""
    try:
        data = request.get_json()
        mode = data.get('mode', 'motion')
        
        if mode not in ['motion', 'gesture', 'head']:
            return jsonify({"error": "Invalid detection mode"}), 400
        
        return jsonify({
            "message": f"Detection mode set to {mode}",
            "mode": mode
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting OpenCV Snake Game Backend...")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /process_frame - Process single frame")
    logger.info("  POST /set_sensitivity - Adjust sensitivity")
    logger.info("  POST /set_detection_mode - Set detection mode")
    logger.info("  WebSocket /socket.io - Real-time frame processing")
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)