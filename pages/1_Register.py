import streamlit as st
from components.styles import apply_global_styles
from components.ui import hero, section_title
from services.request_service import create_registration_request, fetch_all_requests


st.set_page_config(page_title="Registration Request", page_icon="📝", layout="wide")
apply_global_styles()


def get_request_by_username(username):
    requests = fetch_all_requests()
    if not requests:
        return None

    username = username.strip().lower()
    for req in reversed(requests):
        if str(req["username"]).strip().lower() == username:
            return req
    return None


hero(
    "Registration Request",
    "Register as a student or teacher. Student requests go to the Teacher Dashboard, "
    "while teacher requests go to the Admin Panel for approval."
)

section_title("Fill Your Details")

with st.container():
    st.markdown('<div class="form-shell">', unsafe_allow_html=True)

    with st.form("registration_form", clear_on_submit=False):
        c1, c2 = st.columns(2)

        with c1:
            full_name = st.text_input("Full Name")
            username = st.text_input("Choose Username")
            password = st.text_input("Password", type="password")
            email = st.text_input("Email Address")
            role = st.selectbox("Register As", ["student", "teacher"])
            course = st.text_input("Course / Department")

            if role == "student":
                roll_number = st.text_input("Roll Number")
            else:
                roll_number = ""

        with c2:
            if role == "student":
                year_semester = st.selectbox(
                    "Year / Semester",
                    [
                        "1st Semester", "2nd Semester", "3rd Semester",
                        "4th Semester", "5th Semester", "6th Semester"
                    ]
                )
                section = st.text_input("Section")
            else:
                year_semester = "N/A"
                section = "N/A"

            phone = st.text_input("Phone Number")
            reason = st.text_area("Why do you want access to this portal?")
            agree = st.checkbox("I confirm that the above details are correct.")

        submitted = st.form_submit_button("Send Registration Request")

        if submitted:
            required_fields = [full_name, username, password, email, role, course, phone, reason]

            if role == "student":
                required_fields.append(year_semester)
                required_fields.append(roll_number)

            if not all(required_fields) or not agree:
                st.error("Please fill all required details and confirm the checkbox.")
            else:
                success, message = create_registration_request(
                    full_name.strip(),
                    username.strip(),
                    password,
                    email.strip(),
                    roll_number.strip(),
                    course.strip(),
                    year_semester.strip(),
                    section.strip(),
                    phone.strip(),
                    reason.strip(),
                    role.strip()
                )

                if success:
                    route_text = "Teacher Dashboard" if role == "student" else "Admin Panel"
                    st.success(message)
                    st.markdown(f"""
                    <div class="pending-box">
                        <b>Request sent successfully.</b><br>
                        Your {role.title()} request has been submitted and routed to the <b>{route_text}</b> for approval.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(message)

    st.markdown("</div>", unsafe_allow_html=True)


section_title("Check Approval Status")
check_username = st.text_input("Enter your username to check request status")

if check_username:
    req = get_request_by_username(check_username)

    if req is None:
        st.info("No registration request found for this username.")
    else:
        status = str(req["status"]).strip().lower()
        reviewer = str(req["reviewedby"]).strip() if req["reviewedby"] else ""
        comment = str(req["reviewcomment"]).strip() if req["reviewcomment"] else ""
        req_role = str(req["role"]).strip().title() if req.get("role") else "User"

        if status == "approved":
            st.markdown(f"""
            <div class="allow-box">
                <b>{req_role} Registration Approved</b><br>
                You can now login to the Smart Classroom portal.<br>
                Reviewed by: {reviewer if reviewer else "Teacher/Admin"}
            </div>
            """, unsafe_allow_html=True)

        elif status == "rejected":
            st.markdown(f"""
            <div class="reject-box">
                <b>{req_role} Registration Rejected</b><br>
                {f"Comment: {comment}" if comment else "Please contact teacher/admin."}
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div class="pending-box">
                <b>{req_role} Approval Pending</b><br>
                Your request is still under review.
            </div>
            """, unsafe_allow_html=True)