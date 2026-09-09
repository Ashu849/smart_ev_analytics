"""
Smart EV Charging Station Analytics System
============================================
STEP 2: Data Cleaning & Feature Engineering (Pandas + NumPy)

Demonstrates, on the raw CSVs produced by generate_data.py:
    - read_csv, head, info, describe, shape
    - isnull / duplicated detection
    - dropna / fillna (missing value handling)
    - drop_duplicates
    - boolean indexing / filtering impossible values
    - string cleaning (case normalization)
    - merge (joining sessions with stations/customers/vehicles/chargers)
    - apply / map for feature engineering
    - datetime feature extraction (hour, day_of_week, is_weekend)

Outputs a single clean, merged, analysis-ready CSV:
    data/processed/ev_sessions_clean.csv
"""

import pandas as pd
import numpy as np
import os

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


def load_raw_tables():
    stations = pd.read_csv(f"{RAW_DIR}/stations.csv")
    chargers = pd.read_csv(f"{RAW_DIR}/chargers.csv")
    customers = pd.read_csv(f"{RAW_DIR}/customers.csv")
    vehicles = pd.read_csv(f"{RAW_DIR}/vehicles.csv")
    sessions = pd.read_csv(f"{RAW_DIR}/charging_sessions.csv", parse_dates=["start_time", "end_time"])
    return stations, chargers, customers, vehicles, sessions


def inspect(df, name):
    print(f"\n--- {name} ---")
    print("shape:", df.shape)
    print("nulls:\n", df.isnull().sum()[df.isnull().sum() > 0])
    print("duplicate rows:", df.duplicated().sum())


def clean_customers(customers):
    # Normalize inconsistent casing in 'city'
    customers["city"] = customers["city"].str.strip().str.title()
    return customers


def clean_sessions(sessions):
    before = len(sessions)

    # 1. Remove exact duplicate rows
    sessions = sessions.drop_duplicates()

    # 2. Remove impossible values (negative or zero duration)
    sessions = sessions[sessions["charging_duration_minutes"] > 0]

    # 3. Handle missing numeric values -> fill with column median
    numeric_cols_to_fill = ["energy_consumed_kwh", "station_utilization"]
    for col in numeric_cols_to_fill:
        sessions[col] = sessions[col].fillna(sessions[col].median())

    # 4. Handle missing categorical values -> fill with mode / "Unknown"
    sessions["payment_method"] = sessions["payment_method"].fillna(
        sessions["payment_method"].mode()[0]
    )

    after = len(sessions)
    print(f"\nCleaned sessions: {before:,} -> {after:,} rows "
          f"({before - after:,} removed as duplicates/invalid)")

    return sessions.reset_index(drop=True)


def engineer_features(sessions):
    # Datetime features
    sessions["date"] = sessions["start_time"].dt.date
    sessions["hour"] = sessions["start_time"].dt.hour
    sessions["day_of_week"] = sessions["start_time"].dt.day_name()
    sessions["month"] = sessions["start_time"].dt.month_name()
    sessions["is_weekend"] = sessions["start_time"].dt.dayofweek.isin([5, 6]).astype(int)
    sessions["is_peak_hour"] = sessions["hour"].isin([8, 9, 18, 19, 20]).astype(int)

    # SOC gap (NumPy vectorized arithmetic)
    sessions["soc_gap"] = sessions["target_soc"] - sessions["initial_soc"]

    return sessions


def merge_all(sessions, stations, chargers, customers, vehicles):
    df = sessions.merge(
        stations[["station_id", "station_name", "city", "total_chargers"]],
        on="station_id", how="left"
    )
    df = df.merge(
        customers[["customer_id", "customer_type", "city"]].rename(
            columns={"city": "customer_city"}
        ),
        on="customer_id", how="left"
    )
    df = df.merge(
        vehicles[["vehicle_id", "vehicle_type", "vehicle_model", "battery_capacity_kwh"]],
        on="vehicle_id", how="left"
    )
    return df


def apply_customer_segment(sessions):
    """
    Business segmentation without ML: rule-based logic using .apply()
    demonstrating the 'Apply' syllabus topic.
    """
    session_counts = sessions.groupby("customer_id")["session_id"].count()

    def segment(x):
        if x < 5:
            return "Occasional"
        elif x <= 20:
            return "Regular"
        else:
            return "Power User"

    seg_map = session_counts.apply(segment)
    sessions["customer_segment"] = sessions["customer_id"].map(seg_map)
    return sessions


if __name__ == "__main__":
    stations, chargers, customers, vehicles, sessions = load_raw_tables()

    for name, df in [("stations", stations), ("chargers", chargers),
                      ("customers", customers), ("vehicles", vehicles),
                      ("sessions (raw)", sessions)]:
        inspect(df, name)

    customers = clean_customers(customers)
    sessions = clean_sessions(sessions)
    sessions = engineer_features(sessions)
    sessions = apply_customer_segment(sessions)

    merged = merge_all(sessions, stations, chargers, customers, vehicles)

    inspect(merged, "final merged dataset")

    out_path = f"{PROCESSED_DIR}/ev_sessions_clean.csv"
    merged.to_csv(out_path, index=False)
    print(f"\n✅ Clean, merged, analysis-ready dataset saved to: {out_path}")
    print(f"   Final shape: {merged.shape}")
