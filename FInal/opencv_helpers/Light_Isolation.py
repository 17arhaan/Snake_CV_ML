#Light_Isolation.py
import cv2
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
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        cx = x + w // 2
        cy = y + h // 2
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
            previous_direction = current_direction
    cv2.imshow("Tracking UV Light", result)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()