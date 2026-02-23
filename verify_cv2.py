import cv2
import os

cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
print(f"Cascade path: {cascade_path}")
print(f"Exists: {os.path.exists(cascade_path)}")

if os.path.exists(cascade_path):
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print("Error: CascadeClassifier is empty!")
    else:
        print("Success: CascadeClassifier loaded.")
else:
    print("Error: Cascade file not found!")
