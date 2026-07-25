from db import get_all_users_by_role, delete_user_by_username, is_user_approved


def _row_to_student_dict(row):
    if row is None:
        return None

    try:
        keys = row.keys()
        username = row["username"] if "username" in keys else ""
        full_name = (
            row["full_name"]
            if "full_name" in keys
            else (username or "Unknown Student")
        )

        return {
            "id": row["id"] if "id" in keys else None,
            "full_name": full_name,
            "username": username,
            "role": row["role"] if "role" in keys else "student",
            "approved": row["approved"] if "approved" in keys else 0,
        }
    except Exception:
        if isinstance(row, dict):
            return {
                "id": row.get("id"),
                "full_name": row.get("full_name") or row.get("fullname") or row.get("username") or "Unknown Student",
                "username": row.get("username", ""),
                "role": row.get("role", "student"),
                "approved": row.get("approved", 0),
            }

        return {
            "id": None,
            "full_name": str(row),
            "username": "",
            "role": "student",
            "approved": 0,
        }


def fetch_all_students():
    rows = get_all_users_by_role("student")
    return [_row_to_student_dict(row) for row in rows]


def remove_student(username):
    return delete_user_by_username(username, role="student")


def check_student_approval(username):
    return is_user_approved(username)