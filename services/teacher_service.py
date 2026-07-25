from datetime import datetime
import os

import numpy as np
import pandas as pd
import streamlit as st

from db import (
    get_pending_requests_by_role,
    get_all_users_by_role,
    delete_user_by_username,
)
from utils.constants import KNOWN_FACES_DIR
from utils.helpers import load_attendance_csv, save_attendance_csv, build_latest_daily_df


def _empty_attendance_df():
    return pd.DataFrame(columns=["Name", "Date", "Time", "Status"])


def _normalize_attendance_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or not isinstance(df, pd.DataFrame):
        return _empty_attendance_df()

    df = df.copy()
    if df.empty and len(df.columns) == 0:
        return _empty_attendance_df()

    df.columns = [str(col).strip() for col in df.columns]

    rename_map = {
        "name": "Name",
        "date": "Date",
        "time": "Time",
        "status": "Status",
    }
    df.columns = [rename_map.get(c.lower(), c) for c in df.columns]

    for col in ["Name", "Date", "Time", "Status"]:
        if col not in df.columns:
            df[col] = ""

    df = df[["Name", "Date", "Time", "Status"]].copy()

    for col in ["Name", "Date", "Time", "Status"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df = df[df["Name"] != ""].copy()
    return df.reset_index(drop=True)


def _row_to_dict(row):
    if row is None:
        return {}

    if isinstance(row, dict):
        return dict(row)

    try:
        return dict(row)
    except Exception:
        pass

    try:
        return {key: row[key] for key in row.keys()}
    except Exception:
        return {}


def _rows_to_dict_list(rows):
    if not rows:
        return []
    return [_row_to_dict(row) for row in rows]


@st.cache_data(ttl=120)
def _get_known_students():
    students = []
    if not os.path.exists(KNOWN_FACES_DIR):
        return students

    for file_name in os.listdir(KNOWN_FACES_DIR):
        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            name = os.path.splitext(file_name)[0].strip()
            if name:
                students.append(name)

    return sorted(list(set(students)))


def _initialize_today_absent_records():
    df = _normalize_attendance_df(load_attendance_csv())
    all_students = _get_known_students()
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    if not all_students:
        return df

    existing_today = df[df["Date"] == today].copy() if not df.empty else _empty_attendance_df()
    existing_names = set()

    if not existing_today.empty:
        existing_names = set(
            existing_today["Name"].astype(str).str.strip().str.lower().tolist()
        )

    new_rows = []
    for student in all_students:
        if student.strip().lower() not in existing_names:
            new_rows.append(
                {
                    "Name": student,
                    "Date": today,
                    "Time": now_time,
                    "Status": "Absent",
                }
            )

    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        save_attendance_csv(df)
        clear_teacher_caches()

    return _normalize_attendance_df(df)


@st.cache_data(ttl=30)
def get_latest_daily_df():
    raw_df = _normalize_attendance_df(load_attendance_csv())
    latest_df = build_latest_daily_df(raw_df)
    latest_df = _normalize_attendance_df(latest_df)
    return latest_df


def get_today_snapshot():
    _initialize_today_absent_records()
    latest_df = get_latest_daily_df()
    today = datetime.now().strftime("%Y-%m-%d")
    all_students = _get_known_students()

    today_df = latest_df[latest_df["Date"] == today].copy() if not latest_df.empty else _empty_attendance_df()
    existing_names = set()

    if not today_df.empty:
        existing_names = set(
            today_df["Name"].astype(str).str.strip().str.lower().tolist()
        )

    now_time = datetime.now().strftime("%H:%M:%S")
    missing_rows = []
    for student in all_students:
        if student.strip().lower() not in existing_names:
            missing_rows.append(
                {
                    "Name": student,
                    "Date": today,
                    "Time": now_time,
                    "Status": "Absent",
                }
            )

    if missing_rows:
        today_df = pd.concat([today_df, pd.DataFrame(missing_rows)], ignore_index=True)

    today_df = _normalize_attendance_df(today_df)

    if not today_df.empty:
        today_df["Status"] = today_df["Status"].replace("", "Absent")
        today_df["Status"] = today_df["Status"].apply(
            lambda x: "Present" if str(x).strip().lower() == "present" else "Absent"
        )
        today_df = today_df.sort_values(by=["Name"]).reset_index(drop=True)

    present_today = int(today_df["Status"].eq("Present").sum()) if not today_df.empty else 0
    absent_today = int(today_df["Status"].eq("Absent").sum()) if not today_df.empty else len(all_students)
    total_students = len(all_students)

    return today_df, present_today, absent_today, total_students, latest_df


@st.cache_data(ttl=30)
def build_attendance_rate_table(latest_df):
    latest_df = _normalize_attendance_df(latest_df)
    all_students = _get_known_students()
    rows = []

    for student in all_students:
        if latest_df.empty:
            present = absent = total = 0
        else:
            student_df = latest_df[
                latest_df["Name"].astype(str).str.strip().str.lower()
                == student.strip().lower()
            ].copy()

            present = int(
                student_df["Status"].astype(str).str.lower().eq("present").sum()
            )
            absent = int(
                student_df["Status"].astype(str).str.lower().eq("absent").sum()
            )
            total = present + absent

        percentage = round((present / total) * 100, 2) if total > 0 else 0.0

        rows.append(
            {
                "Name": student,
                "Present": present,
                "Absent": absent,
                "Total Days": total,
                "Attendance %": percentage,
            }
        )

    if rows:
        return (
            pd.DataFrame(rows)
            .sort_values(by=["Attendance %", "Name"], ascending=[True, True])
            .reset_index(drop=True)
        )

    return pd.DataFrame(
        columns=["Name", "Present", "Absent", "Total Days", "Attendance %"]
    )


def safe_unique_student_count(df):
    df = _normalize_attendance_df(df)
    if df.empty or "Name" not in df.columns:
        return 0

    return (
        df["Name"]
        .astype(str)
        .str.strip()
        .replace("", np.nan)
        .dropna()
        .nunique()
    )


@st.cache_data(ttl=30)
def build_daily_trend_data(latest_df):
    latest_df = _normalize_attendance_df(latest_df)
    if latest_df.empty:
        return pd.DataFrame(columns=["Date", "Status", "Count"])

    grouped = latest_df.groupby(["Date", "Status"]).size().reset_index(name="Count")
    return grouped


@st.cache_data(ttl=30)
def build_student_percentage_data(rate_df):
    if rate_df is None or rate_df.empty:
        return pd.DataFrame(columns=["Name", "Attendance %"])

    return rate_df.sort_values(by="Attendance %", ascending=False).copy()


@st.cache_data(ttl=30)
def get_teacher_dashboard_data():
    students = _rows_to_dict_list(get_all_users_by_role("student"))
    requests = _rows_to_dict_list(get_pending_requests_by_role("student"))

    today_df, present_today, absent_today, total_students, latest_df = get_today_snapshot()
    rate_df = build_attendance_rate_table(latest_df)

    low_attendance_df = (
        rate_df[rate_df["Attendance %"] < 75].copy()
        if not rate_df.empty
        else pd.DataFrame(columns=["Name", "Present", "Absent", "Total Days", "Attendance %"])
    )

    latest_date = (
        latest_df["Date"].max()
        if not latest_df.empty and "Date" in latest_df.columns
        else "No data"
    )
    total_records = len(latest_df)
    csv_student_count = safe_unique_student_count(latest_df)

    daily_trend_df = build_daily_trend_data(latest_df)
    student_pct_df = build_student_percentage_data(rate_df)

    return {
        "students": students,
        "requests": requests,
        "today_df": today_df,
        "present_today": present_today,
        "absent_today": absent_today,
        "total_students": total_students,
        "latest_df": latest_df,
        "rate_df": rate_df,
        "low_attendance_df": low_attendance_df,
        "latest_date": latest_date,
        "total_records": total_records,
        "csv_student_count": csv_student_count,
        "daily_trend_df": daily_trend_df,
        "student_pct_df": student_pct_df,
    }


def clear_teacher_caches():
    _get_known_students.clear()
    get_latest_daily_df.clear()
    build_attendance_rate_table.clear()
    build_daily_trend_data.clear()
    build_student_percentage_data.clear()
    get_teacher_dashboard_data.clear()


def delete_student(username):
    result = delete_user_by_username(username, role="student")
    clear_teacher_caches()
    return result