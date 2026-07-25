import streamlit as st
from services.auth_service import change_password_for_logged_in_user


def render_change_password_section():
    if "show_change_password" not in st.session_state:
        st.session_state["show_change_password"] = False

    if not st.session_state.get("show_change_password", False):
        return

    st.markdown("""
    <div class="glass-card" style="padding: 20px; margin-bottom: 20px;">
        <h3 style="margin-bottom: 10px;">🔑 Change Password</h3>
        <p style="color: #666; margin-bottom: 0;">
            Update your account password securely.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("change_password_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")

        with col2:
            confirm_password = st.text_input("Confirm New Password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Update Password", use_container_width=True)

        if submitted:
            username = st.session_state.get("username", "").strip()

            success, message = change_password_for_logged_in_user(
                username=username,
                current_password=current_password,
                new_password=new_password,
                confirm_password=confirm_password
            )

            if success:
                st.success(message)
                st.session_state["show_change_password"] = False
            else:
                st.error(message)