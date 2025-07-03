import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Tuple, List
import time
from collections import deque

class AdvancedMotionDetector:
    """Advanced computer vision motion detection for Snake game"""
    
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        
        # Configure MediaPipe models
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7
        )
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7
        )
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7
        )
        
        # Motion tracking
        self.prev_frame = None
        self.motion_history = deque(maxlen=10)
        self.direction_history = deque(maxlen=5)
        
        # Timing controls
        self.last_direction_time = 0
        self.direction_cooldown = 0.6
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0
        
        # Calibration
        self.center_position = None
        self.calibration_frames = 0
        self.is_calibrated = False
        
        # Detection parameters
        self.motion_threshold = 30
        self.gesture_confidence = 0.8
        
    def calibrate(self, frame: np.ndarray) -> bool:
        """Calibrate the detector with user's neutral position"""
        if self.calibration_frames < 30:  # Calibrate for 30 frames
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                nose = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
                h, w = frame.shape[:2]
                
                if self.center_position is None:
                    self.center_position = [nose.x * w, nose.y * h]
                else:
                    # Average the position
                    self.center_position[0] = (self.center_position[0] + nose.x * w) / 2
                    self.center_position[1] = (self.center_position[1] + nose.y * h) / 2
                
                self.calibration_frames += 1
                
        if self.calibration_frames >= 30:
            self.is_calibrated = True
            return True
            
        return False
    
    def detect_hand_gestures(self, frame: np.ndarray) -> Optional[str]:
        """Detect hand gestures for game control"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        current_time = time.time()
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                gesture = self._classify_hand_gesture(hand_landmarks, frame.shape)
                if gesture:
                    self.last_gesture_time = current_time
                    return gesture
        
        return None
    
    def _classify_hand_gesture(self, landmarks, frame_shape) -> Optional[str]:
        """Classify hand gesture based on landmarks"""
        h, w = frame_shape[:2]
        
        # Get key landmarks
        wrist = landmarks.landmark[0]
        thumb_tip = landmarks.landmark[4]
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]
        
        # Convert to pixel coordinates
        points = {
            'wrist': (wrist.x * w, wrist.y * h),
            'thumb': (thumb_tip.x * w, thumb_tip.y * h),
            'index': (index_tip.x * w, index_tip.y * h),
            'middle': (middle_tip.x * w, middle_tip.y * h),
            'ring': (ring_tip.x * w, ring_tip.y * h),
            'pinky': (pinky_tip.x * w, pinky_tip.y * h)
        }
        
        # Gesture recognition logic
        return self._recognize_gesture_pattern(points)
    
    def _recognize_gesture_pattern(self, points: dict) -> Optional[str]:
        """Recognize gesture patterns"""
        wrist = points['wrist']
        index = points['index']
        middle = points['middle']
        thumb = points['thumb']
        
        # Pointing gesture detection
        index_extended = index[1] < wrist[1] - 30  # Index finger up
        middle_folded = middle[1] > wrist[1] - 10   # Middle finger down
        
        if index_extended and middle_folded:
            # Determine pointing direction
            dx = index[0] - wrist[0]
            dy = index[1] - wrist[1]
            
            if abs(dx) > abs(dy):
                return "LEFT" if dx < -50 else "RIGHT" if dx > 50 else None
            else:
                return "UP" if dy < -50 else "DOWN" if dy > 30 else None
        
        # Fist gesture (pause)
        all_folded = all(
            points[finger][1] > wrist[1] - 20 
            for finger in ['index', 'middle', 'ring', 'pinky']
        )
        if all_folded:
            return "PAUSE"
        
        # Open palm (reset)
        all_extended = all(
            points[finger][1] < wrist[1] - 20 
            for finger in ['thumb', 'index', 'middle', 'ring', 'pinky']
        )
        if all_extended:
            return "RESET"
        
        return None
    
    def detect_head_movement(self, frame: np.ndarray) -> Optional[str]:
        """Detect head movement for direction control"""
        if not self.is_calibrated:
            return None
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        current_time = time.time()
        if current_time - self.last_direction_time < self.direction_cooldown:
            return None
        
        if results.pose_landmarks:
            nose = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            h, w = frame.shape[:2]
            
            current_pos = [nose.x * w, nose.y * h]
            
            # Calculate movement from calibrated center
            dx = current_pos[0] - self.center_position[0]
            dy = current_pos[1] - self.center_position[1]
            
            # Threshold for movement detection
            threshold = min(w, h) * 0.08
            
            if abs(dx) > abs(dy) and abs(dx) > threshold:
                direction = "LEFT" if dx < 0 else "RIGHT"
                self.last_direction_time = current_time
                return direction
            elif abs(dy) > threshold:
                direction = "UP" if dy < 0 else "DOWN"
                self.last_direction_time = current_time
                return direction
        
        return None
    
    def detect_eye_blink(self, frame: np.ndarray) -> bool:
        """Detect eye blink for pause functionality"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Eye landmarks for blink detection
                left_eye_top = face_landmarks.landmark[159]
                left_eye_bottom = face_landmarks.landmark[145]
                right_eye_top = face_landmarks.landmark[386]
                right_eye_bottom = face_landmarks.landmark[374]
                
                # Calculate eye aspect ratios
                left_ear = abs(left_eye_top.y - left_eye_bottom.y)
                right_ear = abs(right_eye_top.y - right_eye_bottom.y)
                
                # Blink threshold
                blink_threshold = 0.01
                
                if left_ear < blink_threshold and right_ear < blink_threshold:
                    return True
        
        return False
    
    def detect_optical_flow(self, frame: np.ndarray) -> Optional[str]:
        """Detect motion using optical flow"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        current_time = time.time()
        if current_time - self.last_direction_time < self.direction_cooldown:
            return None
        
        if self.prev_frame is not None:
            # Calculate dense optical flow
            flow = cv2.calcOpticalFlowPyrLK(
                self.prev_frame, gray, None, None,
                winSize=(21, 21),
                maxLevel=3,
                criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01)
            )
            
            # Create a grid of points to track
            h, w = gray.shape
            y, x = np.mgrid[h//4:3*h//4:20, w//4:3*w//4:20].reshape(2, -1).astype(int)
            points = np.vstack((x, y)).T.reshape(-1, 1, 2).astype(np.float32)
            
            if len(points) > 0:
                # Track points
                next_points, status, error = cv2.calcOpticalFlowPyrLK(
                    self.prev_frame, gray, points, None
                )
                
                # Filter good points
                good_new = next_points[status == 1]
                good_old = points[status == 1]
                
                if len(good_new) > 10:
                    # Calculate average motion
                    motion_vectors = good_new - good_old
                    avg_motion = np.mean(motion_vectors, axis=0)
                    
                    # Determine direction
                    dx, dy = avg_motion[0]
                    threshold = 3.0
                    
                    if abs(dx) > abs(dy) and abs(dx) > threshold:
                        direction = "RIGHT" if dx > 0 else "LEFT"
                        self.last_direction_time = current_time
                        return direction
                    elif abs(dy) > threshold:
                        direction = "DOWN" if dy > 0 else "UP"
                        self.last_direction_time = current_time
                        return direction
        
        self.prev_frame = gray.copy()
        return None
    
    def process_frame(self, frame: np.ndarray, detection_mode: str = 'motion') -> dict:
        """Process frame and return detection results"""
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        results = {
            'direction': None,
            'gesture': None,
            'blink': False,
            'calibrated': self.is_calibrated,
            'timestamp': time.time()
        }
        
        # Calibration phase
        if not self.is_calibrated:
            results['calibrated'] = self.calibrate(frame)
            return results
        
        # Detection based on mode
        if detection_mode == 'gesture':
            gesture = self.detect_hand_gestures(frame)
            results['gesture'] = gesture
            if gesture in ['LEFT', 'RIGHT', 'UP', 'DOWN']:
                results['direction'] = gesture
                
        elif detection_mode == 'head':
            results['direction'] = self.detect_head_movement(frame)
            
        elif detection_mode == 'motion':
            results['direction'] = self.detect_optical_flow(frame)
        
        # Always check for blink (universal pause)
        results['blink'] = self.detect_eye_blink(frame)
        
        return results
    
    def reset_calibration(self):
        """Reset calibration for new user"""
        self.center_position = None
        self.calibration_frames = 0
        self.is_calibrated = False
        self.prev_frame = None
        self.motion_history.clear()
        self.direction_history.clear()
    
    def adjust_sensitivity(self, sensitivity: int):
        """Adjust motion detection sensitivity (1-100)"""
        self.motion_threshold = max(1, min(100, sensitivity))
        self.direction_cooldown = 0.3 + (sensitivity / 100) * 0.7  # 0.3-1.0 seconds