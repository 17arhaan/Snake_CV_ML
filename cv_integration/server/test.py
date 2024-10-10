#test.py
import cv2
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        b, g, r = frame[y, x]
        rgb = (r, g, b)
        print(f"Clicked position: ({x}, {y})")
        print(f"RGB value: {rgb}")
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = f"RGB: {rgb}"
        cv2.putText(frame, text, (x, y - 10), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow('Camera Feed', frame)
camera = cv2.VideoCapture(0)
cv2.namedWindow('Camera Feed')
cv2.setMouseCallback('Camera Feed', click_event)
while True:
    ret, frame = camera.read()
    if not ret:
        print("Error: Could not read frame.")
        break
    cv2.imshow('Camera Feed', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
camera.release()
cv2.destroyAllWindows()
