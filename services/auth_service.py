from db import authenticate_user, change_user_password


def login_user(username, password):
    user = authenticate_user(username, password)

    if not user:
        return False, "Invalid username or password.", None

    return True, "Login successful.", user


def change_password_for_logged_in_user(username, current_password, new_password, confirm_password):
    username = username.strip()

    if not username:
        return False, "User session not found."

    if not current_password.strip():
        return False, "Please enter current password."

    if not new_password.strip():
        return False, "Please enter new password."

    if not confirm_password.strip():
        return False, "Please confirm new password."

    if new_password != confirm_password:
        return False, "New password and confirm password do not match."

    return change_user_password(username, current_password, new_password)