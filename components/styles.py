import streamlit as st


def apply_global_styles():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #eef4ff 0%, #f8fbff 45%, #ffffff 100%);
    }

    .block-container {
        max-width: 1250px;
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }

    .hero {
        background: linear-gradient(135deg, #0f172a, #1d4ed8);
        padding: 2.2rem;
        border-radius: 24px;
        color: white;
        box-shadow: 0 16px 38px rgba(29, 78, 216, 0.18);
        margin-bottom: 1rem;
    }

    .hero h1, .hero h2 {
        font-size: 2.4rem;
        margin-bottom: 0.5rem;
        color: white;
    }

    .hero p {
        color: #dbeafe;
        font-size: 1.03rem;
        line-height: 1.7;
        margin-bottom: 0;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    .feature-card,
    .card,
    .metric-box,
    .form-shell {
        background: white;
        padding: 1.25rem;
        border-radius: 18px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
        border: 1px solid #e5e7eb;
    }

    .feature-card h3,
    .card h3,
    .card h4 {
        color: #0f172a;
        margin-bottom: 0.45rem;
    }

    .feature-card p,
    .card p {
        color: #475569;
        line-height: 1.6;
        margin-bottom: 0.3rem;
    }

    .metric-box {
        text-align: center;
    }

    .metric-box h3 {
        color: #334155;
        margin-bottom: 0.35rem;
        font-size: 1.02rem;
    }

    .metric-box h2 {
        color: #1d4ed8;
        margin-bottom: 0.2rem;
        font-size: 2rem;
        font-weight: 800;
    }

    .small-note {
        color: #64748b;
        font-size: 0.9rem;
    }

    .status-box,
    .student-highlight,
    .readonly-box,
    .pending-box,
    .reject-box,
    .allow-box {
        padding: 1rem 1.2rem;
        border-radius: 16px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .status-box,
    .student-highlight {
        background: linear-gradient(135deg, #eff6ff, #ffffff);
        border: 1px solid #bfdbfe;
        color: #1e3a8a;
    }

    .readonly-box {
        background: linear-gradient(135deg, #f8fafc, #ffffff);
        border: 1px solid #cbd5e1;
        color: #334155;
    }

    .pending-box {
        background: linear-gradient(135deg, #fff7ed, #ffffff);
        border: 1px solid #fdba74;
        color: #9a3412;
    }

    .reject-box {
        background: linear-gradient(135deg, #fef2f2, #ffffff);
        border: 1px solid #fca5a5;
        color: #b91c1c;
    }

    .allow-box {
        background: linear-gradient(135deg, #ecfdf5, #ffffff);
        border: 1px solid #86efac;
        color: #166534;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.72rem 1.2rem;
        font-weight: 600;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
        color: white;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 12px !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%);
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)