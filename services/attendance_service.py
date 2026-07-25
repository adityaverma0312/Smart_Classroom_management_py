import pandas as pd
import streamlit as st

from utils.helpers import (
    load_attendance_csv,
    save_attendance_csv,
    build_latest_daily_df,
    normalize_lower,
)
from utils.constants import ATTENDANCE_REQUIRED_COLUMNS


def _empty_attendance_df():
    return pd.DataFrame(columns=ATTENDANCE_REQUIRED_COLUMNS)


@st.cache_data(ttl=30)
def get_attendance_df():
    return load_attendance_csv()


@st.cache_data(ttl=30)
def get_latest_attendance_df():
    df = load_attendance_csv()
    return build_latest_daily_df(df)


@st.cache_data(ttl=30)
def get_total_students():
    df = load_attendance_csv()
    if df.empty or "Name" not in df.columns:
        return 0
    return int(df["Name"].astype(str).str.strip().replace("", pd.NA).dropna().nunique())


@st.cache_data(ttl=30)
def get_overall_summary():
    df = get_latest_attendance_df()

    if df.empty:
        return {
            "present": 0,
            "absent": 0,
            "total": 0,
            "percentage": 0.0,
        }

    status_series = df["Status"].astype(str).str.strip().str.lower()
    present = int(status_series.eq("present").sum())
    absent = int(status_series.eq("absent").sum())
    total = present + absent
    percentage = round((present / total) * 100, 2) if total > 0 else 0.0

    return {
        "present": present,
        "absent": absent,
        "total": total,
        "percentage": percentage,
    }


@st.cache_data(ttl=30)
def get_student_attendance(student_name, username=None):
    df = get_latest_attendance_df()

    if df.empty:
        return _empty_attendance_df()

    student_name_key = normalize_lower(student_name)
    username_key = normalize_lower(username) if username else None

    filtered_df = df[
        df["Name"].astype(str).str.strip().str.lower().eq(student_name_key)
    ].copy()

    if filtered_df.empty and username_key:
        filtered_df = df[
            df["Name"].astype(str).str.strip().str.lower().eq(username_key)
        ].copy()

    return filtered_df.reset_index(drop=True)


@st.cache_data(ttl=30)
def get_student_summary(student_name, username=None):
    student_df = get_student_attendance(student_name, username)

    if student_df.empty:
        return {
            "df": _empty_attendance_df(),
            "present": 0,
            "absent": 0,
            "total": 0,
            "percentage": 0.0,
        }

    status_series = student_df["Status"].astype(str).str.strip().str.lower()
    present = int(status_series.eq("present").sum())
    absent = int(status_series.eq("absent").sum())
    total = present + absent
    percentage = round((present / total) * 100, 2) if total > 0 else 0.0

    return {
        "df": student_df,
        "present": present,
        "absent": absent,
        "total": total,
        "percentage": percentage,
    }


def _clear_attendance_caches():
    get_attendance_df.clear()
    get_latest_attendance_df.clear()
    get_total_students.clear()
    get_overall_summary.clear()
    get_student_attendance.clear()
    get_student_summary.clear()
    get_attendance_by_date.clear()
    get_present_students_by_date.clear()
    get_absent_students_by_date.clear()


def mark_or_update_attendance(student_name, date, time, status):
    df = load_attendance_csv()

    if df.empty:
        df = _empty_attendance_df()

    student_name = str(student_name).strip()
    date = str(date).strip()
    time = str(time).strip()
    status = str(status).strip().title()

    mask = (
        df["Name"].astype(str).str.strip().str.lower().eq(student_name.lower())
        & df["Date"].astype(str).str.strip().eq(date)
    )

    if mask.any():
        df.loc[mask, "Time"] = time
        df.loc[mask, "Status"] = status
    else:
        new_row = pd.DataFrame([{
            "Name": student_name,
            "Date": date,
            "Time": time,
            "Status": status,
        }])
        df = pd.concat([df, new_row], ignore_index=True)

    save_attendance_csv(df)
    _clear_attendance_caches()


@st.cache_data(ttl=30)
def get_attendance_by_date(date):
    df = get_attendance_df()

    if df.empty:
        return _empty_attendance_df()

    date = str(date).strip()
    filtered_df = df[df["Date"].astype(str).str.strip().eq(date)].copy()
    return filtered_df.reset_index(drop=True)


@st.cache_data(ttl=30)
def get_present_students_by_date(date):
    df = get_attendance_by_date(date)

    if df.empty:
        return []

    present_df = df[
        df["Status"].astype(str).str.strip().str.lower().eq("present")
    ].copy()

    if present_df.empty:
        return []

    return sorted(
        present_df["Name"].astype(str).str.strip().replace("", pd.NA).dropna().unique().tolist()
    )


@st.cache_data(ttl=30)
def get_absent_students_by_date(date):
    df = get_attendance_by_date(date)

    if df.empty:
        return []

    absent_df = df[
        df["Status"].astype(str).str.strip().str.lower().eq("absent")
    ].copy()

    if absent_df.empty:
        return []

    return sorted(
        absent_df["Name"].astype(str).str.strip().replace("", pd.NA).dropna().unique().tolist()
    )