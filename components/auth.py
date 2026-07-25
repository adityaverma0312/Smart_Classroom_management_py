import streamlit as st


def initialize_auth_state():
    defaults = {
        "authentication_status": False,
        "user_id": None,
        "name": "",
        "username": "",
        "role": "",
        "show_change_password": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_login_session(user):
    initialize_auth_state()
    st.session_state["authentication_status"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["name"] = user["full_name"]
    st.session_state["username"] = user["username"]
    st.session_state["role"] = user["role"]
    st.session_state["show_change_password"] = False


def clear_login_session():
    keys = [
        "authentication_status",
        "user_id",
        "name",
        "username",
        "role",
        "show_change_password",
    ]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]


def require_login():
    initialize_auth_state()
    if not st.session_state.get("authentication_status", False):
        st.error("Please login first from the Home page.")
        st.stop()


def require_role(role):
    require_login()
    if st.session_state.get("role") != role:
        st.error(f"Access denied. Only {role} can open this page.")
        st.stop()