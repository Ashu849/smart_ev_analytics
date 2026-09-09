"""
Smart EV Charging Station Analytics System
============================================
STEP 3: Exploratory Data Analysis & Business Analytics
        (Matplotlib + Seaborn + Pandas GroupBy/Pivot)

Reads the cleaned dataset and produces a full set of business-question-driven
charts, saved as PNG files in /charts, plus printed KPI summaries.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "..", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 110

df = pd.read_csv(f"{PROCESSED_DIR}/ev_sessions_clean.csv", parse_dates=["start_time", "end_time"])

print("Loaded clean dataset:", df.shape)

# ========================================================================
# EXECUTIVE KPIs
# ========================================================================
print("\n================ EXECUTIVE SUMMARY ================")
print(f"Total sessions:              {len(df):,}")
print(f"Total revenue (INR):         {df['cost_inr'].sum():,.2f}")
print(f"Total energy delivered kWh:  {df['energy_consumed_kwh'].sum():,.2f}")
print(f"Average charging time (min): {df['charging_duration_minutes'].mean():.1f}")
print(f"Average revenue / session:   {df['cost_inr'].mean():.2f}")
print(f"Unique customers served:     {df['customer_id'].nunique():,}")
print(f"Unique stations:             {df['station_id'].nunique()}")
print("=====================================================\n")

# ========================================================================
# 1. Distribution of charging duration
# ========================================================================
plt.figure(figsize=(9, 5))
sns.histplot(df["charging_duration_minutes"], kde=True, color="#1f77b4", bins=40)
plt.title("Distribution of Charging Duration")
plt.xlabel("Minutes")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/01_charging_duration_distribution.png")
plt.close()

# ========================================================================
# 2. Sessions by hour of day (peak hour analysis)
# ========================================================================
hourly = df.groupby("hour")["session_id"].count()
plt.figure(figsize=(10, 5))
sns.barplot(x=hourly.index, y=hourly.values, color="#ff7f0e")
plt.title("Charging Sessions by Hour of Day")
plt.xlabel("Hour")
plt.ylabel("Number of Sessions")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/02_sessions_by_hour.png")
plt.close()

# ========================================================================
# 3. Revenue by station (top 10)
# ========================================================================
station_revenue = (
    df.groupby("station_name")["cost_inr"].sum().sort_values(ascending=False).head(10)
)
plt.figure(figsize=(10, 6))
sns.barplot(x=station_revenue.values, y=station_revenue.index, color="#2ca02c")
plt.title("Top 10 Stations by Revenue")
plt.xlabel("Revenue (INR)")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/03_top_stations_revenue.png")
plt.close()

# ========================================================================
# 4. Charger type comparison (box plot)
# ========================================================================
plt.figure(figsize=(9, 5))
sns.boxplot(data=df, x="charger_type", y="charging_duration_minutes", palette="Set2")
plt.title("Charging Duration by Charger Type")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/04_duration_by_charger_type.png")
plt.close()

# ========================================================================
# 5. Queue length vs charging duration (scatter/relationship)
# ========================================================================
plt.figure(figsize=(9, 5))
sns.scatterplot(
    data=df.sample(3000, random_state=1),
    x="queue_length", y="charging_duration_minutes",
    alpha=0.4, color="#d62728"
)
plt.title("Queue Length vs Charging Duration")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/05_queue_vs_duration.png")
plt.close()

# ========================================================================
# 6. Correlation heatmap
# ========================================================================
numeric_cols = [
    "initial_soc", "target_soc", "soc_gap", "energy_consumed_kwh",
    "charging_duration_minutes", "station_utilization", "queue_length", "cost_inr"
]
plt.figure(figsize=(9, 7))
sns.heatmap(df[numeric_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/06_correlation_heatmap.png")
plt.close()

# ========================================================================
# 7. Pivot table: avg charging duration by hour vs charger type + heatmap
# ========================================================================
pivot = pd.pivot_table(
    df, values="charging_duration_minutes",
    index="hour", columns="charger_type", aggfunc="mean"
)
plt.figure(figsize=(8, 8))
sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu")
plt.title("Avg Charging Duration: Hour vs Charger Type")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/07_pivot_hour_vs_charger.png")
plt.close()

# ========================================================================
# 8. Monthly revenue trend
# ========================================================================
df["month_period"] = df["start_time"].dt.to_period("M").astype(str)
monthly_rev = df.groupby("month_period")["cost_inr"].sum().sort_index()
plt.figure(figsize=(11, 5))
plt.plot(monthly_rev.index, monthly_rev.values, marker="o", color="#9467bd")
plt.xticks(rotation=45)
plt.title("Monthly Revenue Trend")
plt.ylabel("Revenue (INR)")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/08_monthly_revenue_trend.png")
plt.close()

# ========================================================================
# 9. Customer segment distribution
# ========================================================================
seg_counts = df.drop_duplicates("customer_id")["customer_segment"].value_counts()
plt.figure(figsize=(7, 6))
plt.pie(seg_counts.values, labels=seg_counts.index, autopct="%1.1f%%",
        colors=sns.color_palette("pastel"))
plt.title("Customer Segments")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/09_customer_segments.png")
plt.close()

# ========================================================================
# 10. Weekday vs weekend session volume
# ========================================================================
weekday_map = df.groupby("is_weekend")["session_id"].count()
weekday_map.index = ["Weekday", "Weekend"]
plt.figure(figsize=(6, 5))
sns.barplot(x=weekday_map.index, y=weekday_map.values, palette="Set1")
plt.title("Weekday vs Weekend Session Volume")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/10_weekday_vs_weekend.png")
plt.close()

print(f"✅ 10 charts saved to: {CHARTS_DIR}")

# ========================================================================
# BUSINESS SUMMARY TABLES (printed + saved as CSV)
# ========================================================================
station_summary = df.groupby(["station_id", "station_name"]).agg(
    revenue=("cost_inr", "sum"),
    sessions=("session_id", "count"),
    energy_kwh=("energy_consumed_kwh", "sum"),
    avg_duration_min=("charging_duration_minutes", "mean"),
    avg_utilization=("station_utilization", "mean"),
).reset_index().sort_values("revenue", ascending=False)

station_summary.to_csv(f"{CHARTS_DIR}/../data/processed/station_summary.csv", index=False)
print("\nTop 5 stations by revenue:\n", station_summary.head())

charger_summary = df.groupby("charger_type").agg(
    sessions=("session_id", "count"),
    avg_duration=("charging_duration_minutes", "mean"),
    total_revenue=("cost_inr", "sum"),
).reset_index()
charger_summary.to_csv(f"{CHARTS_DIR}/../data/processed/charger_summary.csv", index=False)
print("\nCharger type summary:\n", charger_summary)
