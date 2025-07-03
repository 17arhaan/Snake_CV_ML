import cv2
from flask import Flask, Response
from flask_cors import CORS
import pyautogui
import time

app = Flask(__name__)
CORS(app)

path_points = []

def gen_frames():
    cap = cv2.VideoCapture(0)
    lower_bound = (120, 50, 50)
    upper_bound = (140, 255, 255)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    rect_width = 100
    rect_height = 100
    rectangles = {
        "top": (frame_width // 2 - rect_width // 2, 10, rect_width, rect_height),
        "bottom": (frame_width // 2 - rect_width // 2, frame_height - rect_height - 10, rect_width, rect_height),
        "right": (frame_width - rect_width - 10, frame_height // 2 - rect_height // 2, rect_width, rect_height),
        "left": (10, frame_height // 2 - rect_height // 2, rect_width, rect_height)
    }
    previous_direction = None

    while True:
        ret, frame = cap.read()
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
        mask = cv2.erode(mask, None, iterations=1)
        mask = cv2.dilate(mask, None, iterations=1)
        result = cv2.bitwise_and(frame, frame, mask=mask)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        current_direction = None
        current_time = time.time()

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            cx = x + w // 2
            cy = y + h // 2
            path_points.append((cx, cy, current_time))
            for key, (rx, ry, rw, rh) in rectangles.items():
                if rx < cx < rx + rw and ry < cy < ry + rh:
                    color = (0, 255, 0)
                    if current_direction is None:
                        current_direction = key.capitalize()
                else:
                    color = (0, 0, 255)
                cv2.rectangle(result, (int(rx), int(ry)), (int(rx + rw), int(ry + rh)), color, 2)

            if current_direction and current_direction != previous_direction:
                print(f"Light moved to: {current_direction}")
                if current_direction == "Top":
                    pyautogui.press("up")
                elif current_direction == "Bottom":
                    pyautogui.press("down")
                elif current_direction == "Right":
                    pyautogui.press("right")
                elif current_direction == "Left":
                    pyautogui.press("left")
                previous_direction = current_direction

        path_points[:] = [(px, py, t) for px, py, t in path_points if current_time - t <= 1]
        for i in range(1, len(path_points)):
            cv2.line(result, (path_points[i - 1][0], path_points[i - 1][1]), (path_points[i][0], path_points[i][1]), (0, 255, 255), 2)

        status, buffer = cv2.imencode('.jpg', result)
        frame = buffer.tobytes()    
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)