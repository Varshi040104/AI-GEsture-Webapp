import time
import math
import cv2
import pyautogui
from handTracker import HandTracker

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

detector = HandTracker()
screen_w, screen_h = pyautogui.size()

prev_y = 0
screenshot_start = 0
paused = False
dragging = False

print("Started successfully. Press Q to quit.")

while True:
    success, img = cap.read()
    if not success:
        continue

    img = detector.findHands(img)
    lmList = detector.findPosition(img)

    if len(lmList) >= 21:
        # Finger states
        thumb_up = lmList[4][2] < lmList[3][2]
        index_up = lmList[8][2] < lmList[6][2]
        middle_up = lmList[12][2] < lmList[10][2]
        ring_up = lmList[16][2] < lmList[14][2]
        pinky_up = lmList[20][2] < lmList[18][2]

        cv2.putText(
            img,
            f"T:{thumb_up} I:{index_up} M:{middle_up} R:{ring_up} P:{pinky_up}",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 0),
            2
        )

        thumb_down = not thumb_up
        index_down = not index_up
        middle_down = not middle_up
        ring_down = not ring_up
        pinky_down = not pinky_up

        # Pause/Resume
        fist_pause = index_down and middle_down and ring_down and pinky_down
        resume_pose = index_up and pinky_up and middle_down and ring_down

        if fist_pause:
            paused = True
            prev_y = 0
            screenshot_start = 0
            if dragging:
                pyautogui.mouseUp()
                dragging = False
        elif resume_pose:
            paused = False

        if paused:
            cv2.putText(img, "PAUSED", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Gesture Control", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # Screenshot (open palm hold 2 sec)
        open_palm = thumb_up and index_up and middle_up and ring_up and pinky_up
        if open_palm:
            if screenshot_start == 0:
                screenshot_start = time.time()
            elif time.time() - screenshot_start > 5:
                filename = f"gesture_screenshot_{int(time.time())}.png"
                pyautogui.screenshot(filename)
                print("Screenshot saved:", filename)
                screenshot_start = 0
        else:
            screenshot_start = 0

        # Cursor move
        x_index, y_index = lmList[8][1], lmList[8][2]
        cam_h, cam_w, _ = img.shape
        screen_x = screen_w / cam_w * x_index
        screen_y = screen_h / cam_h * y_index
        pyautogui.moveTo(screen_x, screen_y)

        # Distance thumb-index
        x_thumb, y_thumb = lmList[4][1], lmList[4][2]
        distance = math.hypot(x_thumb - x_index, y_thumb - y_index)

        # Drag (pinch hold)
        if distance < 30:
            if not dragging:
                pyautogui.mouseDown()
                dragging = True
        else:
            if dragging:
                pyautogui.mouseUp()
                dragging = False

        # Scroll (index + middle)
        if index_up and middle_up:
            current_y = lmList[8][2]
            if prev_y != 0:
                if current_y < prev_y:
                    pyautogui.scroll(50)
                elif current_y > prev_y:
                    pyautogui.scroll(-50)
            prev_y = current_y
        else:
            prev_y = 0

    cv2.imshow("Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()