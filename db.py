import sqlite3
import hashlib
from datetime import datetime
import streamlit as st


DB_FILE = "smart_classroom.db"


@st.cache_resource
def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def clear_db_connection_cache():
    get_connection.clear()


def clear_related_caches():
    try:
        from services.request_service import (
            fetch_all_requests,
            fetch_pending_requests,
            fetch_pending_requests_by_role,
        )
        from services.teacher_service import get_teacher_dashboard_data, clear_teacher_caches

        fetch_all_requests.clear()
        fetch_pending_requests.clear()
        fetch_pending_requests_by_role.clear()
        get_teacher_dashboard_data.clear()
        clear_teacher_caches()
    except Exception:
        pass


def hash_password(password):
    return hashlib.sha256(password.strip().encode()).hexdigest()


def _fetchone(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    return cur.fetchone()


def _fetchall(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    return cur.fetchall()


def _execute(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    clear_related_caches()
    return cur


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('teacher', 'student', 'admin')),
            approved INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS registration_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
            roll_number TEXT,
            course TEXT NOT NULL,
            year_semester TEXT NOT NULL,
            section TEXT,
            phone TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            reviewed_by TEXT,
            review_comment TEXT,
            requested_at TEXT NOT NULL
        )
    """)

    defaults = [
        ("Main Teacher", "teacher1", "teacher123", "teacher"),
        ("Main Admin", "admin1", "admin123", "admin"),
    ]

    for full_name, username, password, role in defaults:
        cur.execute("SELECT id FROM users WHERE TRIM(username) = ?", (username,))
        existing = cur.fetchone()

        if not existing:
            cur.execute("""
                INSERT INTO users (full_name, username, password_hash, role, approved, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                full_name,
                username,
                hash_password(password),
                role,
                1,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

    conn.commit()
    clear_related_caches()


def authenticate_user(username, password):
    return _fetchone("""
        SELECT * FROM users
        WHERE TRIM(username) = ? AND password_hash = ? AND approved = 1
    """, (username.strip(), hash_password(password)))


def is_user_approved(username):
    user = _fetchone(
        "SELECT * FROM users WHERE TRIM(username) = ?",
        (username.strip(),)
    )

    if not user:
        return False

    return int(user["approved"]) == 1


def submit_registration_request(full_name, username, password, email, role,
                                roll_number, course, year_semester, section,
                                phone, reason):
    conn = get_connection()
    cur = conn.cursor()

    username = username.strip()

    cur.execute("SELECT * FROM registration_requests WHERE TRIM(username) = ?", (username,))
    existing_request = cur.fetchone()

    cur.execute("SELECT * FROM users WHERE TRIM(username) = ?", (username,))
    existing_user = cur.fetchone()

    if existing_request or existing_user:
        return False, "Username already exists or request already submitted."

    cur.execute("""
        INSERT INTO registration_requests (
            full_name, username, password_hash, email, role, roll_number, course,
            year_semester, section, phone, reason, status, requested_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        full_name.strip(),
        username,
        hash_password(password),
        email.strip(),
        role.strip().lower(),
        roll_number.strip() if roll_number else "",
        course.strip(),
        year_semester.strip(),
        section.strip() if section else "",
        phone.strip(),
        reason.strip(),
        "Pending",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    clear_related_caches()
    return True, "Request submitted successfully."


def get_all_requests():
    return _fetchall("SELECT * FROM registration_requests ORDER BY id DESC")


def get_pending_requests():
    return _fetchall(
        "SELECT * FROM registration_requests WHERE status = 'Pending' ORDER BY id DESC"
    )


def get_pending_requests_by_role(role):
    return _fetchall("""
        SELECT * FROM registration_requests
        WHERE status = 'Pending' AND role = ?
        ORDER BY id DESC
    """, (role.strip().lower(),))


def get_all_users_by_role(role):
    return _fetchall("""
        SELECT * FROM users
        WHERE role = ?
        ORDER BY full_name ASC
    """, (role.strip().lower(),))


def approve_registration_request(request_id, reviewed_by="admin"):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM registration_requests WHERE id = ?", (request_id,))
    req = cur.fetchone()

    if not req:
        return False, "Request not found."

    if req["status"] != "Pending":
        return False, f"Request already {req['status']}."

    req_role = str(req["role"]).strip().lower()
    reviewer_role = str(reviewed_by).strip().lower()

    if req_role == "teacher" and reviewer_role != "admin":
        return False, "Only admin can approve teacher requests."

    if req_role == "student" and reviewer_role not in ["teacher", "admin"]:
        return False, "Only teacher or admin can approve student requests."

    cur.execute("SELECT * FROM users WHERE TRIM(username) = ?", (req["username"].strip(),))
    existing_user = cur.fetchone()

    if existing_user:
        cur.execute("""
            UPDATE registration_requests
            SET status = 'Approved', reviewed_by = ?
            WHERE id = ?
        """, (reviewed_by, request_id))
        conn.commit()
        clear_related_caches()
        return True, "User already exists. Request marked approved."

    cur.execute("""
        INSERT INTO users (full_name, username, password_hash, role, approved, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        req["full_name"],
        req["username"].strip(),
        req["password_hash"],
        req_role,
        1,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    cur.execute("""
        UPDATE registration_requests
        SET status = 'Approved', reviewed_by = ?
        WHERE id = ?
    """, (reviewed_by, request_id))

    conn.commit()
    clear_related_caches()
    return True, f"{req_role.title()} approved successfully."


def reject_registration_request(request_id, reviewed_by="admin", comment="Rejected"):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM registration_requests WHERE id = ?", (request_id,))
    req = cur.fetchone()

    if not req:
        return False, "Request not found."

    if req["status"] != "Pending":
        return False, f"Request already {req['status']}."

    req_role = str(req["role"]).strip().lower()
    reviewer_role = str(reviewed_by).strip().lower()

    if req_role == "teacher" and reviewer_role != "admin":
        return False, "Only admin can reject teacher requests."

    if req_role == "student" and reviewer_role not in ["teacher", "admin"]:
        return False, "Only teacher or admin can reject student requests."

    cur.execute("""
        UPDATE registration_requests
        SET status = 'Rejected', reviewed_by = ?, review_comment = ?
        WHERE id = ?
    """, (reviewed_by, comment.strip(), request_id))

    conn.commit()
    clear_related_caches()
    return True, f"{req_role.title()} request rejected."


def delete_user_by_username(username, role=None):
    conn = get_connection()
    cur = conn.cursor()

    username = username.strip()

    if role:
        cur.execute("""
            SELECT * FROM users
            WHERE TRIM(username) = ? AND role = ?
        """, (username, role.strip().lower()))
    else:
        cur.execute("""
            SELECT * FROM users
            WHERE TRIM(username) = ?
        """, (username,))

    user = cur.fetchone()

    if not user:
        return False, "User not found."

    if role:
        cur.execute("""
            DELETE FROM users
            WHERE TRIM(username) = ? AND role = ?
        """, (username, role.strip().lower()))
    else:
        cur.execute("""
            DELETE FROM users
            WHERE TRIM(username) = ?
        """, (username,))

    cur.execute("""
        DELETE FROM registration_requests
        WHERE TRIM(username) = ?
    """, (username,))

    conn.commit()
    clear_related_caches()
    return True, "User deleted successfully."


def get_user_by_username(username):
    return _fetchone("""
        SELECT * FROM users
        WHERE TRIM(username) = ?
    """, (username.strip(),))


def verify_user_password(username, password):
    row = _fetchone("""
        SELECT password_hash FROM users
        WHERE TRIM(username) = ?
    """, (username.strip(),))

    if not row:
        return False

    return row["password_hash"] == hash_password(password)


def update_user_password(username, new_password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM users
        WHERE TRIM(username) = ?
    """, (username.strip(),))

    user = cur.fetchone()

    if not user:
        return False, "User not found."

    cur.execute("""
        UPDATE users
        SET password_hash = ?
        WHERE TRIM(username) = ?
    """, (hash_password(new_password), username.strip()))

    conn.commit()
    clear_related_caches()
    return True, "Password updated successfully."


def change_user_password(username, current_password, new_password):
    username = username.strip()

    if not verify_user_password(username, current_password):
        return False, "Current password is incorrect."

    if not new_password or len(new_password.strip()) < 6:
        return False, "New password must be at least 6 characters long."

    if hash_password(current_password) == hash_password(new_password):
        return False, "New password must be different from current password."

    return update_user_password(username, new_password.strip())