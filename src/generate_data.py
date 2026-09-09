"""
Smart EV Charging Station Analytics System
============================================
STEP 1 (of the project pipeline): Synthetic Data Generation

This script builds a realistic, relational, multi-table dataset for an EV
charging network operating across Delhi NCR, entirely using Python + NumPy
+ Pandas (no external downloads, no ML).

Tables generated:
    1. stations.csv           - 20 charging stations
    2. chargers.csv           - ~110 chargers spread across stations
    3. customers.csv          - 5,000 customers
    4. vehicles.csv           - 8,000 vehicles owned by customers
    5. charging_sessions.csv  - 60,000 charging sessions (main fact table)
    6. queue_logs.csv         - hourly queue snapshots per station
    7. electricity_cost.csv   - daily electricity consumption & cost per station

Realistic messiness is deliberately injected (missing values, duplicate rows,
inconsistent text casing) so that the cleaning stage in 04_pandas_cleaning
has real work to do, mirroring an actual production dataset.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# ----------------------------------------------------------------------
# Reproducibility
# ----------------------------------------------------------------------
np.random.seed(42)
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)


# ========================================================================
# 1. STATIONS
# ========================================================================
def generate_stations(n_stations=20):
    cities = ["Delhi", "Gurgaon", "Noida", "Faridabad", "Ghaziabad"]
    city_weights = [0.35, 0.30, 0.20, 0.08, 0.07]

    station_names = [
        "Connaught Place", "Cyber Hub", "Sector 18", "DLF Phase 3", "Rajouri Garden",
        "Karol Bagh", "MG Road", "Sector 62", "Dwarka Sector 21", "Saket",
        "Vasant Kunj", "Golf Course Road", "Indirapuram", "Lajpat Nagar", "Sector 29",
        "Greater Kailash", "Udyog Vihar", "Sector 137", "Nehru Place", "Sohna Road"
    ]

    stations = pd.DataFrame({
        "station_id": [f"S{str(i).zfill(3)}" for i in range(1, n_stations + 1)],
        "station_name": station_names[:n_stations],
        "city": np.random.choice(cities, n_stations, p=city_weights),
        "total_chargers": np.random.randint(4, 10, n_stations),
        "latitude": np.round(np.random.uniform(28.35, 28.75, n_stations), 6),
        "longitude": np.round(np.random.uniform(76.95, 77.35, n_stations), 6),
        "opening_date": pd.to_datetime(
            np.random.choice(pd.date_range("2021-01-01", "2023-12-31"), n_stations)
        ).strftime("%Y-%m-%d"),
    })
    return stations


# ========================================================================
# 2. CHARGERS
# ========================================================================
def generate_chargers(stations):
    charger_rows = []
    charger_counter = 1
    charger_type_specs = {
        "AC": {"power_choices": [7, 11, 22], "prob": 0.45},
        "DC": {"power_choices": [30, 60], "prob": 0.35},
        "DC_FAST": {"power_choices": [90, 120, 150], "prob": 0.20},
    }
    types = list(charger_type_specs.keys())
    probs = [charger_type_specs[t]["prob"] for t in types]

    for _, row in stations.iterrows():
        for _ in range(row["total_chargers"]):
            ctype = np.random.choice(types, p=probs)
            power = np.random.choice(charger_type_specs[ctype]["power_choices"])
            status = np.random.choice(
                ["Active", "Active", "Active", "Active", "Under Maintenance"], 1
            )[0]
            charger_rows.append({
                "charger_id": f"C{str(charger_counter).zfill(4)}",
                "station_id": row["station_id"],
                "charger_type": ctype,
                "power_kw": power,
                "status": status,
                "installed_date": row["opening_date"],
            })
            charger_counter += 1
    return pd.DataFrame(charger_rows)


# ========================================================================
# 3. CUSTOMERS
# ========================================================================
def generate_customers(n_customers=5000):
    cities = ["Delhi", "Gurgaon", "Noida", "Faridabad", "Ghaziabad"]
    customer_types = ["Individual", "Individual", "Individual", "Fleet"]

    customers = pd.DataFrame({
        "customer_id": [f"CU{str(i).zfill(5)}" for i in range(1, n_customers + 1)],
        "customer_type": np.random.choice(customer_types, n_customers),
        "city": np.random.choice(cities, n_customers),
        "registration_date": pd.to_datetime(
            np.random.choice(pd.date_range("2022-01-01", "2025-06-30"), n_customers)
        ).strftime("%Y-%m-%d"),
    })

    # Inject some inconsistent casing (real-world messiness) -> to be cleaned later
    messy_idx = np.random.choice(customers.index, size=int(0.03 * n_customers), replace=False)
    customers.loc[messy_idx, "city"] = customers.loc[messy_idx, "city"].str.upper()

    return customers


# ========================================================================
# 4. VEHICLES
# ========================================================================
def generate_vehicles(customers, n_vehicles=8000):
    vehicle_types = ["Hatchback", "Sedan", "SUV", "Two-Wheeler", "Commercial Van"]
    vehicle_type_weights = [0.25, 0.25, 0.20, 0.20, 0.10]
    battery_map = {
        "Hatchback": [30, 35, 40],
        "Sedan": [50, 55, 60],
        "SUV": [70, 75, 82, 100],
        "Two-Wheeler": [2, 3, 4],
        "Commercial Van": [60, 80, 120],
    }
    models = {
        "Hatchback": ["Tata Tiago EV", "MG Comet"],
        "Sedan": ["MG5", "BYD Seal"],
        "SUV": ["Tata Nexon EV", "Mahindra XUV400", "Hyundai Ioniq 5"],
        "Two-Wheeler": ["Ola S1", "Ather 450X"],
        "Commercial Van": ["Tata Ace EV", "Mahindra Treo"],
    }

    owner_ids = np.random.choice(customers["customer_id"], n_vehicles)
    vtypes = np.random.choice(vehicle_types, n_vehicles, p=vehicle_type_weights)

    rows = []
    for i in range(n_vehicles):
        vt = vtypes[i]
        rows.append({
            "vehicle_id": f"V{str(i+1).zfill(5)}",
            "customer_id": owner_ids[i],
            "vehicle_type": vt,
            "vehicle_model": np.random.choice(models[vt]),
            "battery_capacity_kwh": np.random.choice(battery_map[vt]),
            "vehicle_age_years": np.random.randint(0, 5),
        })
    return pd.DataFrame(rows)


# ========================================================================
# 5. CHARGING SESSIONS (main fact table)
# ========================================================================
def generate_sessions(stations, chargers, customers, vehicles, n_sessions=60000):
    date_range = pd.date_range("2025-01-01", "2025-12-31", freq="D")

    # Weighted random session dates (slightly more sessions in recent months -> growth trend)
    month_weights = np.linspace(0.6, 1.4, 12)
    day_probs = []
    for d in date_range:
        day_probs.append(month_weights[d.month - 1])
    day_probs = np.array(day_probs)
    day_probs = day_probs / day_probs.sum()
    session_dates = np.random.choice(date_range, n_sessions, p=day_probs)

    # Hour-of-day distribution: peaks at 9-11am and 6-9pm
    hours = np.arange(24)
    hour_weights = np.array([
        1, 1, 1, 1, 1, 2, 4, 6, 8, 9, 8, 6,
        5, 5, 6, 6, 7, 8, 10, 10, 8, 5, 3, 2
    ], dtype=float)
    hour_weights = hour_weights / hour_weights.sum()
    session_hours = np.random.choice(hours, n_sessions, p=hour_weights)
    session_minutes = np.random.randint(0, 60, n_sessions)

    active_chargers = chargers[chargers["status"] == "Active"].reset_index(drop=True)
    charger_choice_idx = np.random.randint(0, len(active_chargers), n_sessions)
    chosen_chargers = active_chargers.iloc[charger_choice_idx].reset_index(drop=True)

    customer_ids = np.random.choice(customers["customer_id"], n_sessions)
    # bias vehicle selection towards the chosen customer's own vehicles where possible
    vehicle_ids = np.random.choice(vehicles["vehicle_id"], n_sessions)
    vehicle_lookup = vehicles.set_index("vehicle_id")["battery_capacity_kwh"].to_dict()

    initial_soc = np.random.randint(5, 60, n_sessions)
    target_soc = np.clip(initial_soc + np.random.randint(20, 70, n_sessions), 0, 100)

    battery_caps = np.array([vehicle_lookup[v] for v in vehicle_ids])
    power_kw = chosen_chargers["power_kw"].values

    energy_kwh = battery_caps * (target_soc - initial_soc) / 100
    ideal_minutes = (energy_kwh / power_kw) * 60

    station_utilization = np.random.uniform(0.2, 0.95, n_sessions)
    queue_length = np.random.poisson(3, n_sessions)

    duration = (
        ideal_minutes * (1 + station_utilization * 0.25)
        + queue_length * 1.5
        + np.random.normal(0, 6, n_sessions)
    )
    duration = np.clip(duration, 8, None)

    # Cost: per-kWh tariff varies by charger type
    tariff_map = {"AC": 12, "DC": 16, "DC_FAST": 20}  # INR per kWh
    tariffs = chosen_chargers["charger_type"].map(tariff_map).values
    cost = np.round(energy_kwh * tariffs, 2)

    payment_methods = np.random.choice(
        ["UPI", "Credit Card", "Debit Card", "Wallet"], n_sessions,
        p=[0.5, 0.2, 0.15, 0.15]
    )

    start_dt = [
        pd.Timestamp(d) + pd.Timedelta(hours=int(h), minutes=int(m))
        for d, h, m in zip(session_dates, session_hours, session_minutes)
    ]
    end_dt = [s + pd.Timedelta(minutes=float(dur)) for s, dur in zip(start_dt, duration)]

    sessions = pd.DataFrame({
        "session_id": np.arange(10001, 10001 + n_sessions),
        "customer_id": customer_ids,
        "vehicle_id": vehicle_ids,
        "station_id": chosen_chargers["station_id"].values,
        "charger_id": chosen_chargers["charger_id"].values,
        "charger_type": chosen_chargers["charger_type"].values,
        "start_time": start_dt,
        "end_time": end_dt,
        "initial_soc": initial_soc,
        "target_soc": target_soc,
        "energy_consumed_kwh": np.round(energy_kwh, 2),
        "charging_duration_minutes": np.round(duration, 1),
        "station_utilization": np.round(station_utilization, 2),
        "queue_length": queue_length,
        "cost_inr": cost,
        "payment_method": payment_methods,
    })

    # ---- Inject realistic messiness for the cleaning stage ----
    # 1. Missing values (~2%) in a few columns
    for col in ["energy_consumed_kwh", "station_utilization", "payment_method"]:
        idx = np.random.choice(sessions.index, size=int(0.02 * n_sessions), replace=False)
        sessions.loc[idx, col] = np.nan

    # 2. Duplicate rows (~0.5%)
    dup_rows = sessions.sample(int(0.005 * n_sessions), random_state=1)
    sessions = pd.concat([sessions, dup_rows], ignore_index=True)

    # 3. A few impossible values (negative duration) to be filtered during cleaning
    bad_idx = np.random.choice(sessions.index, size=15, replace=False)
    sessions.loc[bad_idx, "charging_duration_minutes"] = -5

    return sessions.sample(frac=1, random_state=7).reset_index(drop=True)


# ========================================================================
# 6. QUEUE LOGS (hourly snapshots per station)
# ========================================================================
def generate_queue_logs(stations, n_days=365):
    rows = []
    date_range = pd.date_range("2025-01-01", periods=n_days, freq="D")
    hour_weights = np.array([
        1, 1, 1, 1, 1, 2, 4, 6, 8, 9, 8, 6,
        5, 5, 6, 6, 7, 8, 10, 10, 8, 5, 3, 2
    ], dtype=float)
    hour_weights = hour_weights / hour_weights.max()

    queue_id = 1
    # Sample a subset of station-day-hour combos to keep file size reasonable
    for station_id in stations["station_id"]:
        sample_days = np.random.choice(date_range, size=120, replace=False)
        for day in sample_days:
            for hour in range(0, 24, 3):  # every 3 hours
                base_wait = 5 + hour_weights[hour] * 25
                vehicles_waiting = max(0, int(np.random.poisson(hour_weights[hour] * 6)))
                avg_wait = max(0, np.round(np.random.normal(base_wait, 4), 1))
                rows.append({
                    "queue_id": queue_id,
                    "station_id": station_id,
                    "date": pd.Timestamp(day).strftime("%Y-%m-%d"),
                    "hour": hour,
                    "vehicles_waiting": vehicles_waiting,
                    "avg_wait_time_minutes": avg_wait,
                })
                queue_id += 1
    return pd.DataFrame(rows)


# ========================================================================
# 7. ELECTRICITY COST (daily, per station)
# ========================================================================
def generate_electricity_cost(stations, sessions):
    daily_energy = (
        sessions.dropna(subset=["energy_consumed_kwh"])
        .assign(date=pd.to_datetime(sessions["start_time"]).dt.date)
        .groupby(["station_id", "date"])["energy_consumed_kwh"]
        .sum()
        .reset_index()
    )
    # Add ~10% grid/overhead consumption on top of what was sold
    daily_energy["electricity_consumed_kwh"] = np.round(
        daily_energy["energy_consumed_kwh"] * np.random.uniform(1.05, 1.15, len(daily_energy)), 2
    )
    electricity_price_per_kwh = 8.5  # INR, flat industrial tariff
    daily_energy["electricity_cost_inr"] = np.round(
        daily_energy["electricity_consumed_kwh"] * electricity_price_per_kwh, 2
    )
    daily_energy["date"] = daily_energy["date"].astype(str)
    return daily_energy[["station_id", "date", "electricity_consumed_kwh", "electricity_cost_inr"]]


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print("Generating stations...")
    stations = generate_stations()

    print("Generating chargers...")
    chargers = generate_chargers(stations)

    print("Generating customers...")
    customers = generate_customers()

    print("Generating vehicles...")
    vehicles = generate_vehicles(customers)

    print("Generating charging sessions (this is the big one)...")
    sessions = generate_sessions(stations, chargers, customers, vehicles)

    print("Generating queue logs...")
    queue_logs = generate_queue_logs(stations)

    print("Generating electricity cost table...")
    electricity_cost = generate_electricity_cost(stations, sessions)

    # Save everything
    stations.to_csv(f"{RAW_DIR}/stations.csv", index=False)
    chargers.to_csv(f"{RAW_DIR}/chargers.csv", index=False)
    customers.to_csv(f"{RAW_DIR}/customers.csv", index=False)
    vehicles.to_csv(f"{RAW_DIR}/vehicles.csv", index=False)
    sessions.to_csv(f"{RAW_DIR}/charging_sessions.csv", index=False)
    queue_logs.to_csv(f"{RAW_DIR}/queue_logs.csv", index=False)
    electricity_cost.to_csv(f"{RAW_DIR}/electricity_cost.csv", index=False)

    print("\n✅ All raw CSV files generated in:", RAW_DIR)
    print(f"   stations.csv           -> {len(stations):,} rows")
    print(f"   chargers.csv           -> {len(chargers):,} rows")
    print(f"   customers.csv          -> {len(customers):,} rows")
    print(f"   vehicles.csv           -> {len(vehicles):,} rows")
    print(f"   charging_sessions.csv  -> {len(sessions):,} rows")
    print(f"   queue_logs.csv         -> {len(queue_logs):,} rows")
    print(f"   electricity_cost.csv   -> {len(electricity_cost):,} rows")
