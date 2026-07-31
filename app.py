#Smart Classroom Management System v1.1
import os
import streamlit as st

from db import init_db
from components.styles import apply_global_styles
from components.auth import set_login_session, clear_login_session
from components.sidebar import show_sidebar
from services.auth_service import login_user
from services.attendance_service import get_total_students, get_overall_summary
from services.face_service import get_student_image


st.set_page_config(
    page_title="Smart Classroom",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


def ensure_session_defaults():
    defaults = {
        "authentication_status": False,
        "user_id": None,
        "name": "",
        "username": "",
        "role": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_custom_css():
    st.markdown("""
    <style>
    .main {
        background:
            radial-gradient(circle at top left, rgba(59,130,246,0.10), transparent 28%),
            radial-gradient(circle at top right, rgba(14,165,233,0.10), transparent 26%),
            linear-gradient(180deg, #f8fbff 0%, #eef4ff 55%, #ffffff 100%);
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }

    .hero-wrap {
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 52%, #0ea5e9 100%);
        border-radius: 28px;
        padding: 2rem;
        color: white;
        box-shadow: 0 20px 45px rgba(30, 64, 175, 0.20);
        border: 1px solid rgba(255,255,255,0.10);
        overflow: hidden;
        position: relative;
        margin-bottom: 1rem;
    }

    .hero-wrap::after {
        content: "";
        position: absolute;
        right: -40px;
        top: -40px;
        width: 220px;
        height: 220px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }

    .hero-title {
        font-size: 3.8rem;
        font-weight: 900;
        line-height: 1.02;
        margin-bottom: 0.55rem;
        letter-spacing: -0.045em;
        color: #ffffff;
        text-shadow: 0 6px 18px rgba(15, 23, 42, 0.18);
    }

    .hero-sub {
        font-size: 1.02rem;
        color: #dbeafe;
        line-height: 1.75;
        max-width: 700px;
    }

    .hero-mini {
        display: inline-block;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.18);
        color: #e0f2fe;
        padding: 0.28rem 0.78rem;
        border-radius: 999px;
        font-size: 0.70rem;
        margin-bottom: 0.95rem;
        font-weight: 700;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.10);
        backdrop-filter: blur(6px);
    }

    .glass-card, .feature-box, .info-card, .login-shell, .metric-box, .symbol-card, .route-box {
        background: rgba(255,255,255,0.92);
        border: 1px solid #e2e8f0;
        border-radius: 22px;
        padding: 1.15rem;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
    }

    .feature-box {
        height: 100%;
        transition: 0.25s ease;
    }

    .feature-box:hover {
        transform: translateY(-4px);
        box-shadow: 0 18px 34px rgba(37, 99, 235, 0.10);
        border-color: #bfdbfe;
    }

    .feature-icon {
        font-size: 1.65rem;
        margin-bottom: 0.5rem;
    }

    .feature-title {
        font-size: 1.08rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.35rem;
    }

    .feature-text {
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.7;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 0.9rem;
        margin-bottom: 0.8rem;
    }

    .section-sub {
        color: #475569;
        margin-bottom: 0.9rem;
        line-height: 1.7;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin: 1rem 0 0.4rem 0;
    }

    .chip {
        background: linear-gradient(135deg, #eff6ff, #ffffff);
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 999px;
        padding: 0.5rem 0.85rem;
        font-size: 0.84rem;
        font-weight: 700;
    }

    .metric-box {
        text-align: center;
        padding: 1.2rem 1rem;
    }

    .metric-box h4 {
        color: #475569;
        font-size: 0.92rem;
        margin-bottom: 0.35rem;
        font-weight: 600;
    }

    .metric-box h2 {
        color: #0f172a;
        font-size: 2rem;
        margin: 0;
        font-weight: 800;
    }

    .metric-note {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }

    .summary-box {
        background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
        border: 1px solid #bfdbfe;
        color: #1e3a8a;
        border-radius: 18px;
        padding: 1rem 1.1rem;
        margin-top: 0.8rem;
        margin-bottom: 1rem;
        line-height: 1.75;
    }

    .highlight-list {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
    }

    .highlight-item {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 0.85rem 0.95rem;
        color: #334155;
        line-height: 1.65;
    }

    .symbol-card {
        height: 100%;
    }

    .symbol-line {
        font-size: 0.96rem;
        color: #334155;
        padding: 0.35rem 0;
        border-bottom: 1px dashed #e2e8f0;
    }

    .symbol-line:last-child {
        border-bottom: none;
    }

    .status-strip {
        padding: 0.95rem 1.1rem;
        border-radius: 16px;
        margin: 0.8rem 0;
        line-height: 1.7;
        background: linear-gradient(135deg, #eff6ff, #ffffff);
        border: 1px solid #bfdbfe;
        color: #1e40af;
    }

    .mini-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.55rem;
    }

    .small-text {
        font-size: 0.93rem;
        color: #475569;
        line-height: 1.7;
    }

    .route-box {
        background: linear-gradient(135deg, #f8fafc, #ffffff);
    }

    .stButton > button, .stFormSubmitButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.78rem 1.1rem;
        font-weight: 700;
    }

    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    @media (max-width: 900px) {
        .highlight-list {
            grid-template-columns: 1fr;
        }
        .hero-title {
            font-size: 2.45rem;
            line-height: 1.08;
        }
        .hero-mini {
            font-size: 0.66rem;
            padding: 0.24rem 0.62rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_section_title(title, subtitle=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


def redirect_by_role(user):
    role = str(user["role"]).strip().lower()
    if role == "student":
        st.switch_page("pages/2_Student_Dashboard.py")
    elif role == "teacher":
        st.switch_page("pages/3_Teacher_Dashboard.py")
    elif role == "admin":
        st.switch_page("pages/4_Admin_Panel.py")
    else:
        st.warning("Unknown role found. Please contact admin.")


def render_hero():
    col1, col2 = st.columns([1.45, 0.85], gap="large")

    with col1:
        st.markdown("""
        <div class="hero-wrap">
            <div class="hero-mini">Mini Attendance System</div>
            <div class="hero-title">Smart Classroom</div>
            <div class="hero-sub">
                A smarter, cleaner, and more secure way to manage classroom attendance.
                Smart Classroom is a mini attendance system for academic use. It helps manage attendance records,
                student access, teacher monitoring, admin control, and dashboard-based workflow in one clean platform.
            </div>
            <div class="chip-row">
                <span class="chip">📸 Live Camera</span>
                <span class="chip">✅ Attendance Records</span>
                <span class="chip">👩‍🏫 Teacher Access</span>
                <span class="chip">🛡️ Admin Control</span>
                <span class="chip">📊 Summary Dashboard</span>
                <span class="chip">🔐 Secure Login</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        hero_candidates = [
            "assets/classroom.jpg",
            "assets/classroom.png",
            "assets/smart_classroom.jpg",
            "assets/smart_classroom.png",
            "known_faces/demo.jpg"
        ]

        shown = False
        for path in hero_candidates:
            if os.path.exists(path):
                st.image(path, caption="Smart Classroom Preview", width="stretch")
                shown = True
                break

        if not shown:
            st.markdown("""
            <div class="glass-card" style="min-height: 315px; display:flex; flex-direction:column; justify-content:center;">
                <div class="mini-title">📷 Add a classroom photo</div>
                <div class="small-text">
                    Put any image in <b>assets/classroom.jpg</b> or <b>assets/classroom.png</b> to display a photo here.
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_logged_in_status():
    if st.session_state.get("authentication_status"):
        st.markdown(f"""
        <div class="status-strip">
            <b>Logged in:</b> {st.session_state.get("name", "")}
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Username:</b> {st.session_state.get("username", "")}
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Role:</b> {st.session_state.get("role", "")}
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([0.82, 0.18])
        with c2:
            if st.button("Logout", width="stretch"):
                clear_login_session()
                st.success("Logged out successfully.")
                st.rerun()


def render_overview_metrics():
    render_section_title(
        "Platform Highlights",
        "A quick look at what the Smart Classroom system offers without exposing private records."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="metric-box">
            <h4>🧩 Total Modules</h4>
            <h2>4+</h2>
            <div class="metric-note">Login, Register, Attendance, Dashboard</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="metric-box">
            <h4>👥 User Roles</h4>
            <h2>3</h2>
            <div class="metric-note">Student, Teacher, Admin</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="metric-box">
            <h4>🔐 Access Type</h4>
            <h2>RBAC</h2>
            <div class="metric-note">Role-based secure access</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="metric-box">
            <h4>📸 Smart Support</h4>
            <h2>Yes</h2>
            <div class="metric-note">Photo-friendly and attendance-ready UI</div>
        </div>
        """, unsafe_allow_html=True)


def render_project_summary():
    render_section_title(
        "About Smart Classroom",
        "A compact and useful mini project for attendance management."
    )

    st.markdown("""
    <div class="summary-box">
        <b>Smart Classroom</b> is a mini attendance system that helps manage classroom attendance in a digital and organized way.
        It can maintain attendance records, support secure login, provide role-based access, and help teachers and admins monitor student activity.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="highlight-list">
        <div class="highlight-item">📌 <b>Stores attendance records</b> with date, time, and status.</div>
        <div class="highlight-item">📌 <b>Supports teacher and admin roles</b> with separate dashboards.</div>
        <div class="highlight-item">📌 <b>Improves organization</b> by keeping records clear and structured.</div>
        <div class="highlight-item">📌 <b>Shows attendance summaries</b> through live overview cards.</div>
        <div class="highlight-item">📌 <b>Supports images/photos</b> for a better UI presentation.</div>
        <div class="highlight-item">📌 <b>Provides secure login flow</b> with dashboard redirection.</div>
    </div>
    """, unsafe_allow_html=True)


def render_features():
    render_section_title(
        "What it can do",
        "Main capabilities of the Smart Classroom attendance platform."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📸</div>
            <div class="feature-title">Photo-Friendly Interface</div>
            <div class="feature-text">
                The home page can show a classroom image, and the project also supports student image lookup from your existing face service.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Attendance Summary</div>
            <div class="feature-text">
                It shows total students, present count, absent count, and attendance percentage in a clear dashboard format.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🔐</div>
            <div class="feature-title">Role-Based Access</div>
            <div class="feature-text">
                After login, students, teachers, and admins are redirected to their own dashboard pages automatically.
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_login_section():
    render_section_title(
        "Login Portal",
        "Login securely to continue to your role-based dashboard."
    )

    left, right = st.columns([1.18, 0.82], gap="large")

    with left:
        st.markdown('<div class="login-shell">', unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login")

            if submitted:
                username = username.strip()
                password = password.strip()

                if not username or not password:
                    st.warning("Please enter both username and password.")
                else:
                    success, message, user = login_user(username, password)
                    if success:
                        set_login_session(user)
                        st.success(message)
                        redirect_by_role(user)
                    else:
                        st.error(message)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="route-box">
            <div class="mini-title">📝 New student registration</div>
            <div class="small-text">
                Registration has been moved to a separate page for better security and cleaner home-page design.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        if st.button("Go to Register Page", width="stretch"):
            st.switch_page("pages/1_Register.py")


def render_workflow():
    render_section_title(
        "How it works",
        "Simple workflow of the mini attendance system."
    )

    st.markdown("""
    <div class="highlight-list">
        <div class="highlight-item">1️⃣ User logs in through the secure home page.</div>
        <div class="highlight-item">2️⃣ System checks role and redirects to the correct dashboard.</div>
        <div class="highlight-item">3️⃣ Teacher and admin manage records using their own control pages.</div>
        <div class="highlight-item">4️⃣ Attendance is stored with date, time, and status fields.</div>
        <div class="highlight-item">5️⃣ Summary cards show present, absent, and percentage details.</div>
        <div class="highlight-item">6️⃣ Photos and symbols improve the clarity and attractiveness of the interface.</div>
    </div>
    """, unsafe_allow_html=True)


def main():
    init_db()
    ensure_session_defaults()
    apply_global_styles()
    render_custom_css()
    show_sidebar()

    render_hero()
    render_logged_in_status()
    render_overview_metrics()
    render_project_summary()
    render_features()
    render_login_section()
    render_workflow()


if __name__ == "__main__":
    main()