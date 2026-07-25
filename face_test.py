import face_recognition
import cv2
import os
import numpy as np
import csv
from datetime import datetime

known_face_encodings = []
known_face_names = []

known_dir = "known_faces"
attendance_dir = "attendance"
attendance_file = os.path.join(attendance_dir, "attendance.csv")

os.makedirs(attendance_dir, exist_ok=True)

if not os.path.exists(attendance_file):
    with open(attendance_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Date", "Time", "Status"])

for file in os.listdir(known_dir):
    if file.endswith((".jpg", ".jpeg", ".png")):
        img_path = os.path.join(known_dir, file)
        image = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(file)[0])

video_capture = cv2.VideoCapture(0)

recognized_names = []

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    recognized_names = []

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

        if name != "Unknown":
            recognized_names.append(name)

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Smart Classroom Face Recognition", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        cv2.imwrite("captured.jpg", frame)

        with open(attendance_file, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for name in set(recognized_names):
                writer.writerow([name, current_date, current_time, "Present"])

        print("Photo saved and attendance marked.")

    if key == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()