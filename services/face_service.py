import os
from datetime import datetime

import cv2
import face_recognition
import numpy as np
import pandas as pd
import streamlit as st

from utils.constants import KNOWN_FACES_DIR
from utils.helpers import load_attendance_csv, save_attendance_csv


def get_student_image(student_name=None, username=None):
    if not os.path.exists(KNOWN_FACES_DIR):
        return None

    candidates = []

    if student_name and str(student_name).strip():
        candidates.append(str(student_name).strip())

    if username and str(username).strip():
        candidates.append(str(username).strip())

    for candidate in candidates:
        for ext in (".jpg", ".jpeg", ".png"):
            file_path = os.path.join(KNOWN_FACES_DIR, f"{candidate}{ext}")
            if os.path.exists(file_path):
                return file_path

    candidate_map = {c.lower(): c for c in candidates}

    for file_name in os.listdir(KNOWN_FACES_DIR):
        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            base_name = os.path.splitext(file_name)[0].strip()
            if base_name.lower() in candidate_map:
                return os.path.join(KNOWN_FACES_DIR, file_name)

    return None


@st.cache_resource
def _load_known_faces():
    encodings = []
    names = []

    if not os.path.exists(KNOWN_FACES_DIR):
        return encodings, names

    for file_name in os.listdir(KNOWN_FACES_DIR):
        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            file_path = os.path.join(KNOWN_FACES_DIR, file_name)
            try:
                image = face_recognition.load_image_file(file_path)
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    encodings.append(face_encodings[0])
                    names.append(os.path.splitext(file_name)[0].strip())
            except Exception:
                pass

    return encodings, names


def _clear_related_caches():
    try:
        from services.attendance_service import (
            get_attendance_df,
            get_latest_attendance_df,
            get_total_students,
            get_overall_summary,
            get_student_attendance,
            get_student_summary,
            get_attendance_by_date,
            get_present_students_by_date,
            get_absent_students_by_date,
        )
        from services.teacher_service import (
            get_latest_daily_df,
            build_attendance_rate_table,
            get_teacher_dashboard_data,
        )

        get_attendance_df.clear()
        get_latest_attendance_df.clear()
        get_total_students.clear()
        get_overall_summary.clear()
        get_student_attendance.clear()
        get_student_summary.clear()
        get_attendance_by_date.clear()
        get_present_students_by_date.clear()
        get_absent_students_by_date.clear()
        get_latest_daily_df.clear()
        build_attendance_rate_table.clear()
        get_teacher_dashboard_data.clear()
    except Exception:
        pass


def _mark_present(name: str):
    df = load_attendance_csv()

    required_cols = ["Name", "Date", "Time", "Status"]
    if df.empty:
        df = pd.DataFrame(columns=required_cols)
    else:
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""

    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    df["Name"] = df["Name"].astype(str)
    df["Date"] = df["Date"].astype(str)
    df["Time"] = df["Time"].astype(str)
    df["Status"] = df["Status"].astype(str)

    mask = (
        df["Name"].str.strip().str.lower().eq(name.strip().lower())
        & df["Date"].str.strip().eq(today)
    )

    if mask.any():
        df.loc[mask, "Status"] = "Present"
        df.loc[mask, "Time"] = now_time
    else:
        new_row = pd.DataFrame(
            [
                {
                    "Name": str(name).strip(),
                    "Date": today,
                    "Time": now_time,
                    "Status": "Present",
                }
            ]
        )
        df = pd.concat([df, new_row], ignore_index=True)

    save_attendance_csv(df)
    _clear_related_caches()


def render_live_face_attendance():
    st.markdown(
        '<div class="section-title">Live Face Attendance Capture</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "All students are marked absent by default for today. When a known face "
        "is recognized through the live camera, that student is updated to present."
    )

    known_face_encodings, known_face_names = _load_known_faces()

    if not known_face_names:
        st.warning("No student images found in the known_faces folder.")
        return

    tolerance = st.slider(
        "Face match tolerance (lower = stricter)", 0.30, 0.80, 0.50, 0.05
    )
    camera_index = st.number_input(
        "Camera index", min_value=0, max_value=5, value=0, step=1
    )

    start = st.button("Start Live Camera Attendance")
    stop = st.button("Stop Live Camera")

    if stop:
        st.session_state["stop_camera_loop"] = True
        st.info("Camera stop requested.")

    if start:
        st.session_state["stop_camera_loop"] = False

        cap = cv2.VideoCapture(int(camera_index))
        if not cap.isOpened():
            st.error("Unable to access webcam.")
            return

        frame_placeholder = st.empty()
        status_placeholder = st.empty()
        table_placeholder = st.empty()

        marked_names = set()
        process_this_frame = True
        face_locations = []
        face_names = []
        last_table_df = None

        try:
            from services.teacher_service import get_today_snapshot
            today_df, _, _, _, _ = get_today_snapshot()
            last_table_df = today_df
            table_placeholder.dataframe(today_df, use_container_width=True)
        except Exception:
            pass

        while cap.isOpened():
            if st.session_state.get("stop_camera_loop", False):
                st.session_state["stop_camera_loop"] = False
                break

            ret, frame = cap.read()
            if not ret:
                status_placeholder.error("Failed to read webcam frame.")
                break

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            if process_this_frame:
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(
                    rgb_small_frame, face_locations
                )
                face_names = []

                for face_encoding in face_encodings:
                    name = "Unknown"

                    if known_face_encodings:
                        matches = face_recognition.compare_faces(
                            known_face_encodings, face_encoding, tolerance=tolerance
                        )
                        distances = face_recognition.face_distance(
                            known_face_encodings, face_encoding
                        )
                        best_match_index = int(np.argmin(distances))

                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]

                    face_names.append(name)

            process_this_frame = not process_this_frame

            refresh_table = False

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(
                    frame,
                    (left, bottom - 35),
                    (right, bottom),
                    color,
                    cv2.FILLED,
                )
                cv2.putText(
                    frame,
                    name,
                    (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

                if name != "Unknown" and name not in marked_names:
                    _mark_present(name)
                    marked_names.add(name)
                    status_placeholder.success(f"{name} marked present")
                    refresh_table = True

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(
                rgb_frame, channels="RGB", use_container_width=True
            )

            if refresh_table:
                try:
                    from services.teacher_service import get_today_snapshot
                    today_df, _, _, _, _ = get_today_snapshot()
                    last_table_df = today_df
                    table_placeholder.dataframe(today_df, use_container_width=True)
                except Exception:
                    pass
            elif last_table_df is not None:
                table_placeholder.dataframe(last_table_df, use_container_width=True)

        cap.release()
        cv2.destroyAllWindows()