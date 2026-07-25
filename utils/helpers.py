import os
import pandas as pd
from utils.constants import ATTENDANCE_FILE, ATTENDANCE_REQUIRED_COLUMNS


def normalize_text(value):
    return str(value).strip()


def normalize_lower(value):
    return str(value).strip().lower()


def ensure_attendance_csv():
    os.makedirs(os.path.dirname(ATTENDANCE_FILE), exist_ok=True)

    if not os.path.exists(ATTENDANCE_FILE):
        pd.DataFrame(columns=ATTENDANCE_REQUIRED_COLUMNS).to_csv(ATTENDANCE_FILE, index=False)


def load_attendance_csv():
    ensure_attendance_csv()

    try:
        df = pd.read_csv(ATTENDANCE_FILE, skipinitialspace=True)

        if df.empty:
            return pd.DataFrame(columns=ATTENDANCE_REQUIRED_COLUMNS)

        df.columns = [str(col).strip() for col in df.columns]

        for col in ATTENDANCE_REQUIRED_COLUMNS:
            if col not in df.columns:
                df[col] = ""

        df = df[ATTENDANCE_REQUIRED_COLUMNS].copy()

        for col in ATTENDANCE_REQUIRED_COLUMNS:
            df[col] = df[col].fillna("").astype(str).str.strip()

        if "Name" in df.columns:
            df = df[df["Name"] != ""].copy()

        return df.reset_index(drop=True)

    except Exception:
        return pd.DataFrame(columns=ATTENDANCE_REQUIRED_COLUMNS)


def save_attendance_csv(df):
    os.makedirs(os.path.dirname(ATTENDANCE_FILE), exist_ok=True)

    out_df = df.copy()
    out_df.columns = [str(col).strip() for col in out_df.columns]

    for col in ATTENDANCE_REQUIRED_COLUMNS:
        if col not in out_df.columns:
            out_df[col] = ""

    out_df = out_df[ATTENDANCE_REQUIRED_COLUMNS].copy()

    for col in ATTENDANCE_REQUIRED_COLUMNS:
        out_df[col] = out_df[col].fillna("").astype(str).str.strip()

    out_df.to_csv(ATTENDANCE_FILE, index=False)


def build_latest_daily_df(df):
    if df.empty:
        return pd.DataFrame(columns=ATTENDANCE_REQUIRED_COLUMNS)

    work_df = df.copy()

    work_df["sort_key"] = pd.to_datetime(
        work_df["Date"].astype(str) + " " + work_df["Time"].astype(str),
        errors="coerce"
    )

    work_df = work_df.sort_values(by=["Name", "Date", "sort_key"])
    work_df = work_df.drop_duplicates(subset=["Name", "Date"], keep="last")
    work_df = work_df.drop(columns=["sort_key"], errors="ignore")

    return work_df.reset_index(drop=True)