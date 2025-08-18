# emotion_detector.py
import cv2
from deepface import DeepFace

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_emotion(image):
    """
    Detects the dominant emotion in a given image.
    Args:
        image: NumPy array (BGR format from OpenCV)
    Returns:
        str: Dominant emotion (e.g., 'happy', 'sad') or 'unknown' if no face/emotion detected
    """
    try:
        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Convert grayscale to RGB for DeepFace
        rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            # Use the first detected face
            x, y, w, h = faces[0]
            face_roi = rgb_frame[y:y + h, x:x + w]

            # Perform emotion analysis
            result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
            emotion = result[0]['dominant_emotion']
            return emotion
        else:
            return "unknown"  # No face detected
    except Exception as e:
        print(f"Error in emotion detection: {e}")
        return "unknown"

# For standalone testing
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        emotion = detect_emotion(frame)
        print(f"Detected emotion: {emotion}")
    cap.release()