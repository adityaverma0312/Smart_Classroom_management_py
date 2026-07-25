import streamlit as st

from db import (
    submit_registration_request,
    get_all_requests,
    get_pending_requests,
    get_pending_requests_by_role,
    approve_registration_request,
    reject_registration_request,
)


def _get_value(row, *possible_keys, default=""):
    if row is None:
        return default

    try:
        keys = row.keys()
        for key in possible_keys:
            if key in keys:
                value = row[key]
                return value if value is not None else default
    except Exception:
        pass

    if isinstance(row, dict):
        for key in possible_keys:
            if key in row:
                value = row.get(key)
                return value if value is not None else default

    return default


def _row_to_request_dict(row):
    if row is None:
        return None

    return {
        "id": _get_value(row, "id", default=None),
        "full_name": _get_value(row, "full_name", "fullname", "name"),
        "username": _get_value(row, "username"),
        "email": _get_value(row, "email"),
        "role": str(_get_value(row, "role", default="student")).strip().lower(),
        "roll_number": _get_value(row, "roll_number", "rollnumber"),
        "course": _get_value(row, "course"),
        "year_semester": _get_value(row, "year_semester", "yearsemester"),
        "section": _get_value(row, "section"),
        "phone": _get_value(row, "phone"),
        "reason": _get_value(row, "reason"),
        "status": _get_value(row, "status", default="Pending"),
        "reviewed_by": _get_value(row, "reviewed_by", "reviewedby"),
        "review_comment": _get_value(row, "review_comment", "reviewcomment"),
        "requested_at": _get_value(row, "requested_at", "requestedat"),
    }


def _clear_request_caches():
    fetch_all_requests.clear()
    fetch_pending_requests.clear()
    fetch_pending_requests_by_role.clear()


def create_registration_request(
    full_name,
    username,
    password,
    email,
    roll_number,
    course,
    year_semester,
    section,
    phone,
    reason,
    role
):
    result = submit_registration_request(
        full_name,
        username,
        password,
        email,
        role,
        roll_number,
        course,
        year_semester,
        section,
        phone,
        reason
    )
    _clear_request_caches()
    return result


@st.cache_data(ttl=30)
def fetch_all_requests():
    rows = get_all_requests()
    return [_row_to_request_dict(row) for row in rows]


@st.cache_data(ttl=30)
def fetch_pending_requests():
    rows = get_pending_requests()
    return [_row_to_request_dict(row) for row in rows]


@st.cache_data(ttl=30)
def fetch_pending_requests_by_role(role):
    rows = get_pending_requests_by_role(role)
    return [_row_to_request_dict(row) for row in rows]


def approve_request(request_id, reviewed_by="admin"):
    result = approve_registration_request(request_id, reviewed_by)
    _clear_request_caches()
    return result


def reject_request(request_id, reviewed_by="admin", comment="Rejected"):
    result = reject_registration_request(request_id, reviewed_by, comment)
    _clear_request_caches()
    return result