import streamlit as st
from components.auth import clear_login_session


def show_sidebar():
    with st.sidebar:
        st.markdown("## Smart Classroom")

        if st.session_state.get("authentication_status"):
            st.write(f"**Name:** {st.session_state.get('name', '-')}")
            st.write(f"**Role:** {st.session_state.get('role', '-')}")

            st.markdown("---")

            if st.button("Change Password"):
                st.session_state["show_change_password"] = not st.session_state.get("show_change_password", False)

            if st.button("Logout"):
                clear_login_session()
                st.success("Logged out successfully.")
                st.switch_page("app.py")