import os

import pandas as pd
import plotly.express as px
import streamlit as st

from services.request_service import approve_request, reject_request
from services.teacher_service import delete_student
from utils.constants import KNOWN_FACES_DIR


def _metric_card(title, value, note=""):
    st.markdown(
        f"""
    <div class="metric-box">
        <h3>{title}</h3>
        <h2>{value}</h2>
        <p class="small-note">{note}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_teacher_header(teacher_name: str, data: dict):
    st.markdown(
        f"""
<div class="welcome-strip">
    <h2>👨‍🏫 Welcome, {teacher_name}</h2>
    <p>Manage attendance, monitor classroom records, capture faces using live camera, review reports, and approve student access requests.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Teacher Overview</div>',
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        _metric_card("👨‍🎓 Students", len(data["students"]), "Approved student accounts")
    with k2:
        _metric_card("📄 Records", data["total_records"], "Latest daily records")
    with k3:
        _metric_card("✅ Today Present", data["present_today"], "Recognized today")
    with k4:
        _metric_card("❌ Today Absent", data["absent_today"], "Not seen today")
    with k5:
        _metric_card(
            "📅 Latest Date",
            data["latest_date"],
            f"{data['csv_student_count']} students in CSV",
        )

    st.markdown(
        """
<div class="teacher-highlight">
    <b>Attendance flow:</b> students in <b>known_faces</b> are marked absent for today by default, then the live camera recognizes faces and updates matched students to present automatically.
</div>
""",
        unsafe_allow_html=True,
    )


def render_teacher_metrics(data: dict):
    pass


def render_summary_tab(data: dict):
    if data["total_students"] == 0:
        st.warning("No student images found in known_faces folder.")
        return

    summary_df = pd.DataFrame(
        {
            "Status": ["Present", "Absent"],
            "Count": [data["present_today"], data["absent_today"]],
        }
    )

    t1, t2 = st.columns(2)

    with t1:
        fig_pie = px.pie(
            summary_df,
            values="Count",
            names="Status",
            title="Today's Attendance Distribution",
            hole=0.45,
            color="Status",
            color_discrete_map={"Present": "#22c55e", "Absent": "#ef4444"},
        )
        fig_pie.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

    with t2:
        fig_bar = px.bar(
            summary_df,
            x="Status",
            y="Count",
            title="Today's Present vs Absent",
            text="Count",
            color="Status",
            color_discrete_map={"Present": "#22c55e", "Absent": "#ef4444"},
        )
        fig_bar.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    daily_trend_df = data.get("daily_trend_df")
    if daily_trend_df is not None and not daily_trend_df.empty:
        fig_trend = px.line(
            daily_trend_df,
            x="Date",
            y="Count",
            color="Status",
            markers=True,
            title="Daily Attendance Trend",
            color_discrete_map={"Present": "#16a34a", "Absent": "#dc2626"},
        )
        fig_trend.update_layout(
            template="plotly_white",
            xaxis_title="Date",
            yaxis_title="Students",
            legend_title="Status",
            height=420,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    student_pct_df = data.get("student_pct_df")
    if student_pct_df is not None and not student_pct_df.empty:
        fig_pct = px.bar(
            student_pct_df,
            x="Name",
            y="Attendance %",
            color="Attendance %",
            title="Attendance Percentage by Student",
            color_continuous_scale="Blues",
        )
        fig_pct.update_layout(
            template="plotly_white",
            xaxis_title="Student",
            yaxis_title="Attendance %",
            height=450,
        )
        fig_pct.update_yaxes(range=[0, 100])
        st.plotly_chart(fig_pct, use_container_width=True)

    st.dataframe(data["today_df"], use_container_width=True)


def render_student_tab(data: dict):
    rate_df = data["rate_df"]
    latest_df = data["latest_df"]

    st.markdown(
        '<div class="section-title">Student Details</div>',
        unsafe_allow_html=True,
    )

    if rate_df.empty or "Name" not in rate_df.columns:
        st.info("No student details available.")
        return

    selected_student = st.selectbox("Select student", rate_df["Name"].tolist())
    selected_summary = rate_df[rate_df["Name"] == selected_student].iloc[0]

    selected_history = latest_df[
        latest_df["Name"].astype(str).str.strip().str.lower()
        == selected_student.strip().lower()
    ].copy()

    if not selected_history.empty:
        selected_history = selected_history.sort_values(
            by=["Date", "Time"], ascending=[False, False]
        )

    def _get_student_image(name):
        for ext in [".jpg", ".jpeg", ".png"]:
            path = os.path.join(KNOWN_FACES_DIR, f"{name}{ext}")
            if os.path.exists(path):
                return path
        return None

    with st.expander(f"View Details: {selected_student}", expanded=True):
        c1, c2 = st.columns([1, 2])

        with c1:
            image_path = _get_student_image(selected_student)
            if image_path:
                st.image(
                    image_path,
                    caption=selected_student,
                    use_container_width=True,
                )
            else:
                st.info("No photo available.")

        with c2:
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Present", int(selected_summary["Present"]))
            with m2:
                st.metric("Absent", int(selected_summary["Absent"]))
            with m3:
                st.metric("Total Days", int(selected_summary["Total Days"]))
            with m4:
                st.metric("Attendance %", f'{selected_summary["Attendance %"]}%')

            if not selected_history.empty:
                fig = px.bar(
                    selected_history,
                    x="Date",
                    color="Status",
                    title=f"{selected_student} Attendance History",
                    barmode="group",
                    color_discrete_map={
                        "Present": "#22c55e",
                        "Absent": "#ef4444",
                    },
                )
                fig.update_layout(template="plotly_white", height=400)
                st.plotly_chart(fig, use_container_width=True)

                pie_df = pd.DataFrame(
                    {
                        "Status": ["Present", "Absent"],
                        "Count": [
                            int(selected_summary["Present"]),
                            int(selected_summary["Absent"]),
                        ],
                    }
                )
                pie_fig = px.pie(
                    pie_df,
                    values="Count",
                    names="Status",
                    title=f"{selected_student} Attendance Ratio",
                    hole=0.45,
                    color="Status",
                    color_discrete_map={
                        "Present": "#22c55e",
                        "Absent": "#ef4444",
                    },
                )
                pie_fig.update_layout(template="plotly_white", height=400)
                st.plotly_chart(pie_fig, use_container_width=True)

                st.dataframe(selected_history, use_container_width=True)
            else:
                st.info("No attendance history found.")


def render_request_tab(requests):
    st.markdown(
        '<div class="section-title">Student Registration Requests</div>',
        unsafe_allow_html=True,
    )

    if not requests:
        st.success("No pending registration requests.")
        return

    st.markdown(
        f"""
    <div class="alert-box">
        <b>Pending requests:</b> {len(requests)} student request(s) are waiting for approval.
    </div>
    """,
        unsafe_allow_html=True,
    )

    for req in requests:
        section = req["section"] if req["section"] else "N/A"

        st.markdown(
            f"""
        <div class="request-card">
            <div class="request-title">👤 {req["full_name"]}</div>
            <p><b>Username:</b> {req["username"]}</p>
            <p><b>Email:</b> {req["email"]}</p>
            <p><b>Roll Number:</b> {req["roll_number"]}</p>
            <p><b>Course:</b> {req["course"]}</p>
            <p><b>Year/Semester:</b> {req["year_semester"]}</p>
            <p><b>Section:</b> {section}</p>
            <p><b>Phone:</b> {req["phone"]}</p>
            <p><b>Reason:</b> {req["reason"]}</p>
            <p><b>Requested At:</b> {req["requested_at"]}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        with st.form(key=f"request_action_form_{req['id']}"):
            c1, c2 = st.columns(2)

            with c1:
                approve_clicked = st.form_submit_button(
                    f"Approve {req['username']}",
                    use_container_width=True,
                )

            with c2:
                reject_clicked = st.form_submit_button(
                    f"Reject {req['username']}",
                    use_container_width=True,
                )

            if approve_clicked:
                success, message = approve_request(
                    req["id"],
                    reviewed_by=st.session_state.get("role", "teacher"),
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

            if reject_clicked:
                success, message = reject_request(
                    req["id"],
                    reviewed_by=st.session_state.get("role", "teacher"),
                    comment="Rejected by teacher",
                )
                if success:
                    st.warning(message)
                    st.rerun()
                else:
                    st.error(message)

        st.markdown("---")


def render_alert_tab(low_attendance_df: pd.DataFrame):
    st.markdown(
        '<div class="section-title">Low Attendance Alerts</div>',
        unsafe_allow_html=True,
    )

    if low_attendance_df.empty:
        st.success("No low attendance alerts right now.")
        return

    st.markdown(
        f"""
    <div class="alert-box">
        <b>Alert:</b> {len(low_attendance_df)} student(s) are below 75% attendance.
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.dataframe(
        low_attendance_df,
        use_container_width=True,
        column_config={
            "Attendance %": st.column_config.NumberColumn(
                "Attendance %",
                format="%.2f%%",
            )
        },
    )

    fig_low = px.bar(
        low_attendance_df.sort_values(by="Attendance %"),
        x="Name",
        y="Attendance %",
        text="Attendance %",
        title="Students Below 75% Attendance",
        color="Attendance %",
        color_continuous_scale="Oranges",
    )
    fig_low.update_layout(template="plotly_white", height=430)
    fig_low.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_low, use_container_width=True)


def render_recent_tab(data: dict):
    st.markdown(
        '<div class="section-title">Recent Attendance Records</div>',
        unsafe_allow_html=True,
    )

    latest_df = data["latest_df"]
    rate_df = data["rate_df"]

    if latest_df.empty:
        st.info("No attendance records found yet.")
        return

    recent_df = latest_df.sort_values(
        by=["Date", "Time"], ascending=[False, False]
    ).head(20)
    st.dataframe(recent_df, use_container_width=True)

    overall_df = pd.DataFrame(
        {
            "Status": ["Present", "Absent"],
            "Count": [
                int(rate_df["Present"].sum()) if not rate_df.empty else 0,
                int(rate_df["Absent"].sum()) if not rate_df.empty else 0,
            ],
        }
    )

    fig_overall = px.pie(
        overall_df,
        values="Count",
        names="Status",
        title="Overall Attendance Status",
        hole=0.45,
        color="Status",
        color_discrete_map={"Present": "#16a34a", "Absent": "#dc2626"},
    )
    fig_overall.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig_overall, use_container_width=True)


def render_delete_student_section(students):
    st.subheader("Delete Student")

    if not students:
        st.info("No students found.")
        return

    student_options = {
        f"{student['full_name']} ({student['username']})": student["username"]
        for student in students
    }

    with st.form("delete_student_form"):
        selected_student = st.selectbox(
            "Select student to delete",
            list(student_options.keys())
        )
        confirm = st.checkbox("I confirm I want to delete this student")
        submitted = st.form_submit_button(
            "Delete Selected Student",
            use_container_width=True,
        )

        if submitted:
            if not confirm:
                st.warning("Please confirm before deleting.")
            else:
                username = student_options[selected_student]
                success, message = delete_student(username)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)