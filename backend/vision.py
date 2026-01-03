import cv2
import mediapipe as mp
import numpy as np
import time

try:
    import mediapipe as mp
except ImportError:
    raise RuntimeError("MediaPipe not installed correctly")

mp_face = mp.solutions.face_mesh

class VisionEngine:
    def __init__(self):
        self.face_mesh = mp_face.FaceMesh(refine_landmarks=True)
        self.last_look_time = time.time()
        self.look_away_seconds = 0

    def analyze(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(rgb)

        if not result.multi_face_landmarks:
            return self._response("Proctor Alert", "No Face", 0)

        if len(result.multi_face_landmarks) > 1:
            return self._response("Proctor Alert", "Multiple Faces", len(result.multi_face_landmarks))

        landmarks = result.multi_face_landmarks[0].landmark

        emotion = self.detect_confusion(landmarks)
        gaze = self.detect_gaze(landmarks)

        alert = "OK"
        if gaze != "Center":
            self.look_away_seconds += 1
            if self.look_away_seconds >= 4:
                alert = "Proctor Alert"
        else:
            self.look_away_seconds = 0

        return self._response(emotion, gaze, 1, alert)

    def detect_gaze(self, lm):
        left_eye = lm[33]
        right_eye = lm[263]
        nose = lm[1]

        if nose.x < left_eye.x:
            return "Left"
        if nose.x > right_eye.x:
            return "Right"
        return "Center"

    def detect_confusion(self, lm):
        brow_left = lm[70]
        brow_right = lm[300]
        mouth_left = lm[61]
        mouth_right = lm[291]

        brow_dist = abs(brow_left.y - brow_right.y)
        mouth_width = abs(mouth_left.x - mouth_right.x)

        if brow_dist < 0.01 and mouth_width < 0.04:
            return "Confused"
        if mouth_width > 0.06:
            return "Happy"
        return "Focused"

    def _response(self, emotion, gaze, face_count, alert="OK"):
        return {
            "emotion": emotion,
            "gaze": gaze,
            "face_count": face_count,
            "alert": alert,
            "timestamp": time.time()
        }
