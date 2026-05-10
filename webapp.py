import cv2
import streamlit as st
from handTracker import HandTracker

st.title("✋ AI Gesture Recognition Web App")
st.write(
    "Control the computer using hand gestures. "
    "Show the gestures below to perform different actions."
)

st.markdown("""
## 📖 How to Use

| Gesture | Meaning | Action |
|--------|--------|--------|
| 🖐️ Open Palm | Show all fingers | Pause / Resume Detection |
| 👆 Index Finger | One finger up | Move Cursor |
| 🤏 Pinch | Thumb and index touch | Left Click |
| ✌️ Two Fingers | Two fingers up | Scroll Up |
| 🤟 Three Fingers | Three fingers up | Scroll Down |
| 👍 Thumbs Up | Thumb only | Start Detection |
| ✊ Closed Fist | No fingers open | Stop Detection |
""")

st.set_page_config(page_title="AI Gesture Control", layout="wide")
st.title("✋ AI Gesture Recognition Web App")
st.write("Real-time hand tracking and gesture recognition using MediaPipe and Streamlit.")

run = st.checkbox("Start Camera")
frame_placeholder = st.empty()
gesture_placeholder = st.empty()

if run:
    cap = cv2.VideoCapture(0)
    detector = HandTracker()

    while run:
        success, img = cap.read()
        if not success:
            st.error("Could not access webcam.")
            break

        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        gesture_name = "No Hand Detected"

        if len(lmList) >= 21:
            thumb_up = lmList[4][2] < lmList[3][2]
            index_up = lmList[8][2] < lmList[6][2]
            middle_up = lmList[12][2] < lmList[10][2]
            ring_up = lmList[16][2] < lmList[14][2]
            pinky_up = lmList[20][2] < lmList[18][2]

            if all([thumb_up, index_up, middle_up, ring_up, pinky_up]):
                gesture_name = "Open Palm (Screenshot Gesture)"
            elif index_up and middle_up and not ring_up and not pinky_up:
                gesture_name = "Scroll Gesture"
            elif not index_up and not middle_up and not ring_up and not pinky_up:
                gesture_name = "Fist (Pause Gesture)"
            elif index_up and pinky_up and not middle_up and not ring_up:
                gesture_name = "Resume Gesture"
            elif index_up and not middle_up and not ring_up and not pinky_up:
                gesture_name = "Cursor Movement"
            else:
                gesture_name = "Gesture Detected"

        gesture_placeholder.success(f"Detected Gesture: {gesture_name}")
        frame_placeholder.image(img, channels="BGR")

    cap.release()