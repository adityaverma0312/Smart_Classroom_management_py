import streamlit as st

from components.sidebar import show_sidebar
from components.styles import apply_global_styles
from components.change_password_ui import render_change_password_section
from components.teacher_ui import (
    render_teacher_header,
    render_summary_tab,
    render_student_tab,
    render_request_tab,
    render_alert_tab,
    render_recent_tab,
    render_delete_student_section,
)
from services.teacher_service import get_teacher_dashboard_data
from services.face_service import render_live_face_attendance


st.set_page_config(page_title="Teacher Dashboard", page_icon="👨‍🏫", layout="wide")

apply_global_styles()
show_sidebar()
render_change_password_section()


def teacher_guard():
    if not st.session_state.get("authentication_status", False):
        st.markdown("""
        <div class="glass-card">
            <h2>🔒 Login Required</h2>
            <p>Please log in to access the Teacher Dashboard.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    if st.session_state.get("role") != "teacher":
        st.markdown("""
        <div class="glass-card">
            <h2>⛔ Access Denied</h2>
            <p>Only teachers can open this page.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()


teacher_guard()

if "teacher_face_tab_enabled" not in st.session_state:
    st.session_state["teacher_face_tab_enabled"] = False

data = get_teacher_dashboard_data()

render_teacher_header(st.session_state.get("name", "Teacher"), data)

tabs = st.tabs([
    "Today Summary",
    "Live Face Capture",
    "Student Details",
    "Approval Requests",
    "Alerts",
    "Recent Records"
])

with tabs[0]:
    render_summary_tab(data)

with tabs[1]:
    st.markdown("### Live Face Capture")
    st.write("Start live face attendance only when needed to keep dashboard loading faster.")

    if not st.session_state["teacher_face_tab_enabled"]:
        if st.button("Open Live Face Attendance"):
            st.session_state["teacher_face_tab_enabled"] = True
            st.rerun()
    else:
        render_live_face_attendance()

with tabs[2]:
    render_student_tab(data)

with tabs[3]:
    render_request_tab(data["requests"])

with tabs[4]:
    render_alert_tab(data["low_attendance_df"])

with tabs[5]:
    render_recent_tab(data)

render_delete_student_section(data["students"])