import streamlit as st

from components.styles import apply_global_styles
from components.auth import require_role
from components.sidebar import show_sidebar
from components.change_password_ui import render_change_password_section
from components.ui import section_title
from services.request_service import (
    fetch_pending_requests_by_role,
    approve_request,
    reject_request,
)
from db import get_all_users_by_role, delete_user_by_username


st.set_page_config(page_title="Admin Panel", page_icon="🛡️", layout="wide")
apply_global_styles()
show_sidebar()
render_change_password_section()
require_role("admin")

st.markdown("""
<div class="hero">
    <h2>Admin Panel</h2>
    <p>Approve teacher requests, reject requests, and manage users.</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["Teacher Requests", "Students", "Teachers"])

with tabs[0]:
    section_title("Pending Teacher Registration Requests")
    requests = fetch_pending_requests_by_role("teacher")

    if not requests:
        st.info("No pending teacher requests found.")
    else:
        for req in requests:
            req_id = req.get("id", "-")
            req_fullname = req.get("fullname", "Unknown User")
            req_username = req.get("username", "-")
            req_status = str(req.get("status", "Unknown")).strip()
            req_role = req.get("role", "teacher")

            with st.expander(f"{req_id} - {req_fullname} ({req_username}) - {req_role} - {req_status}"):
                st.write(f"Email: {req.get('email', '-')}")
                st.write(f"Course: {req.get('course', '-')}")
                st.write(f"Year/Semester: {req.get('yearsemester', '-')}")
                st.write(f"Section: {req.get('section', '-')}")
                st.write(f"Phone: {req.get('phone', '-')}")
                st.write(f"Reason: {req.get('reason', '-')}")
                st.write(f"Reviewed By: {req.get('reviewedby') or '-'}")
                st.write(f"Comment: {req.get('reviewcomment') or '-'}")

                if req_status.lower() == "pending":
                    c1, c2 = st.columns(2)

                    with c1:
                        if st.button("Approve", key=f"admin_approve_{req_id}"):
                            success, msg = approve_request(
                                req_id,
                                reviewed_by=st.session_state.get("role", "admin")
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                    with c2:
                        if st.button("Reject", key=f"admin_reject_{req_id}"):
                            success, msg = reject_request(
                                req_id,
                                reviewed_by=st.session_state.get("role", "admin"),
                                comment="Rejected by admin"
                            )
                            if success:
                                st.warning(msg)
                                st.rerun()
                            else:
                                st.error(msg)

with tabs[1]:
    section_title("Approved Students")
    students = get_all_users_by_role("student")

    if not students:
        st.info("No students found.")
    else:
        for student in students:
            student_fullname = student["full_name"]
            student_username = student["username"]
            student_approved = student["approved"]

            c1, c2 = st.columns([4, 1])

            with c1:
                st.markdown(f"""
                <div class="card">
                    <h4>{student_fullname}</h4>
                    <p>Username: {student_username}</p>
                    <p>Approved: {student_approved}</p>
                    <p>Role: student</p>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                if st.button("Delete", key=f"delete_student_{student_username}"):
                    success, msg = delete_user_by_username(student_username, role="student")
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

with tabs[2]:
    section_title("Approved Teachers")
    teachers = get_all_users_by_role("teacher")

    if not teachers:
        st.info("No teachers found.")
    else:
        for teacher in teachers:
            teacher_fullname = teacher["full_name"]
            teacher_username = teacher["username"]
            teacher_approved = teacher["approved"]

            c1, c2 = st.columns([4, 1])

            with c1:
                st.markdown(f"""
                <div class="card">
                    <h4>{teacher_fullname}</h4>
                    <p>Username: {teacher_username}</p>
                    <p>Approved: {teacher_approved}</p>
                    <p>Role: teacher</p>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                if st.button("Delete", key=f"delete_teacher_{teacher_username}"):
                    success, msg = delete_user_by_username(teacher_username, role="teacher")
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)