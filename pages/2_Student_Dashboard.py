import streamlit as st
import pandas as pd
import plotly.express as px

from components.styles import apply_global_styles
from components.auth import require_role
from components.sidebar import show_sidebar
from components.change_password_ui import render_change_password_section
from components.ui import section_title
from services.student_service import check_student_approval
from services.attendance_service import get_student_summary, get_overall_summary
from services.face_service import get_student_image


st.set_page_config(page_title="Student Dashboard", page_icon="🎓", layout="wide")
apply_global_styles()
show_sidebar()
render_change_password_section()
require_role("student")


username = st.session_state.get("username", "").strip()
student_name = st.session_state.get("name", "").strip()

allowed = check_student_approval(username)
if not allowed:
    st.markdown(
        """
        <div class="pending-box">
            <b>Access not allowed yet.</b><br>
            Your account is not approved yet.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

student_data = get_student_summary(student_name, username)
student_df = student_data["df"]
present_count = student_data["present"]
absent_count = student_data["absent"]
total_days = student_data["total"]
attendance_pct = float(student_data["percentage"])
overall = get_overall_summary()
overall_pct = float(overall["percentage"])

st.markdown(
    f"""
    <div class="hero">
        <h2>Welcome, {student_name}</h2>
        <p>This is your student dashboard. You can only view your own attendance records and class summary.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f"""
        <div class="metric-box">
            <h3>Present</h3>
            <h2>{present_count}</h2>
            <p class="small-note">Your present days</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f"""
        <div class="metric-box">
            <h3>Absent</h3>
            <h2>{absent_count}</h2>
            <p class="small-note">Your absent days</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        f"""
        <div class="metric-box">
            <h3>Total Days</h3>
            <h2>{total_days}</h2>
            <p class="small-note">Recorded days</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f"""
        <div class="metric-box">
            <h3>Attendance %</h3>
            <h2>{attendance_pct:.2f}%</h2>
            <p class="small-note">Your ratio</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

tabs = st.tabs(["Profile", "My Attendance", "Charts", "Overall"])

with tabs[0]:
    c1, c2 = st.columns([1, 2])

    with c1:
        img = get_student_image(student_name=student_name, username=username)

        if img:
            st.image(img, caption=student_name or username, use_container_width=True)
        else:
            st.info("No profile image found.")

    with c2:
        st.markdown(
            f"""
            <div class="card">
                <h3>{student_name}</h3>
                <p><b>Username:</b> {username}</p>
                <p><b>Attendance Percentage:</b> {attendance_pct:.2f}%</p>
                <p><b>Overall Class Attendance:</b> {overall_pct:.2f}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="readonly-box">
                This dashboard is read-only for students. You can only view your records.
            </div>
            """,
            unsafe_allow_html=True,
        )

with tabs[1]:
    section_title("My Attendance")
    if student_df.empty:
        st.warning("No attendance record found.")
    else:
        display_df = student_df.sort_values(by=["Date", "Time"], ascending=[False, False])
        st.dataframe(display_df, use_container_width=True)

with tabs[2]:
    summary_df = pd.DataFrame(
        {
            "Status": ["Present", "Absent"],
            "Count": [present_count, absent_count],
        }
    )

    c1, c2 = st.columns(2)

    with c1:
        fig1 = px.pie(
            summary_df,
            values="Count",
            names="Status",
            title="My Attendance Ratio",
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        fig2 = px.bar(
            summary_df,
            x="Status",
            y="Count",
            title="My Present vs Absent",
            color="Status",
        )
        st.plotly_chart(fig2, use_container_width=True)

with tabs[3]:
    overall_df = pd.DataFrame(
        {
            "Status": ["Present", "Absent"],
            "Count": [overall["present"], overall["absent"]],
        }
    )

    c1, c2 = st.columns(2)

    with c1:
        fig3 = px.pie(
            overall_df,
            values="Count",
            names="Status",
            title="Overall Attendance Ratio",
        )
        st.plotly_chart(fig3, use_container_width=True)

    with c2:
        fig4 = px.bar(
            overall_df,
            x="Status",
            y="Count",
            title="Overall Present vs Absent",
            color="Status",
        )
        st.plotly_chart(fig4, use_container_width=True)