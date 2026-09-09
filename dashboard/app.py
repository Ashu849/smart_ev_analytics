"""
Smart EV Charging Station Analytics System
============================================
STEP 4: Interactive Streamlit Dashboard (NO ML — pure descriptive/business analytics)

Run with:
    streamlit run dashboard/app.py

Pages:
    1. Executive Overview
    2. Station Performance
    3. Charger Analytics
    4. Customer Analytics
    5. Revenue & Profitability
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="Smart EV Charging Analytics", layout="wide", page_icon="🚗")

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "ev_sessions_clean.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["start_time", "end_time"])
    return df

df = load_data()

st.sidebar.title("🚗 Smart EV Charging")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Executive Overview", "📍 Station Performance", "⚡ Charger Analytics",
     "👥 Customer Analytics", "💰 Revenue & Profitability"]
)

# ========================================================================
# PAGE 1 — EXECUTIVE OVERVIEW
# ========================================================================
if page == "🏠 Executive Overview":
    st.title("Executive Overview")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Sessions", f"{len(df):,}")
    col2.metric("Total Revenue", f"₹{df['cost_inr'].sum():,.0f}")
    col3.metric("Energy Delivered", f"{df['energy_consumed_kwh'].sum():,.0f} kWh")
    col4.metric("Avg Charging Time", f"{df['charging_duration_minutes'].mean():.1f} min")
    col5.metric("Active Stations", df["station_id"].nunique())

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Sessions by Hour")
        hourly = df.groupby("hour")["session_id"].count()
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=hourly.index, y=hourly.values, ax=ax, color="#1f77b4")
        ax.set_xlabel("Hour"); ax.set_ylabel("Sessions")
        st.pyplot(fig)

    with c2:
        st.subheader("Revenue by Station (Top 10)")
        rev = df.groupby("station_name")["cost_inr"].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=rev.values, y=rev.index, ax=ax, color="#2ca02c")
        st.pyplot(fig)

    st.subheader("Monthly Revenue Trend")
    monthly = df.copy()
    monthly["month"] = monthly["start_time"].dt.to_period("M").astype(str)
    monthly_rev = monthly.groupby("month")["cost_inr"].sum().sort_index()
    st.line_chart(monthly_rev)

# ========================================================================
# PAGE 2 — STATION PERFORMANCE
# ========================================================================
elif page == "📍 Station Performance":
    st.title("Station Performance")

    station = st.selectbox("Select a station", sorted(df["station_name"].unique()))
    sdf = df[df["station_name"] == station]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sessions", f"{len(sdf):,}")
    col2.metric("Revenue", f"₹{sdf['cost_inr'].sum():,.0f}")
    col3.metric("Avg Charging Time", f"{sdf['charging_duration_minutes'].mean():.1f} min")
    col4.metric("Avg Utilization", f"{sdf['station_utilization'].mean()*100:.1f}%")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Hourly Demand")
        hourly = sdf.groupby("hour")["session_id"].count()
        st.bar_chart(hourly)
    with c2:
        st.subheader("Charger Type Split")
        ct = sdf["charger_type"].value_counts()
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(ct.values, labels=ct.index, autopct="%1.0f%%")
        st.pyplot(fig)

    st.subheader("Daily Session Volume")
    daily = sdf.groupby(sdf["start_time"].dt.date)["session_id"].count()
    st.line_chart(daily)

# ========================================================================
# PAGE 3 — CHARGER ANALYTICS
# ========================================================================
elif page == "⚡ Charger Analytics":
    st.title("Charger Analytics")

    summary = df.groupby("charger_type").agg(
        sessions=("session_id", "count"),
        avg_duration=("charging_duration_minutes", "mean"),
        total_revenue=("cost_inr", "sum"),
        total_energy=("energy_consumed_kwh", "sum"),
    ).reset_index()

    st.dataframe(summary, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sessions by Charger Type")
        st.bar_chart(summary.set_index("charger_type")["sessions"])
    with c2:
        st.subheader("Avg Duration by Charger Type")
        st.bar_chart(summary.set_index("charger_type")["avg_duration"])

    st.subheader("Duration Distribution by Charger Type")
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.boxplot(data=df, x="charger_type", y="charging_duration_minutes", ax=ax)
    st.pyplot(fig)

# ========================================================================
# PAGE 4 — CUSTOMER ANALYTICS
# ========================================================================
elif page == "👥 Customer Analytics":
    st.title("Customer Analytics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", f"{df['customer_id'].nunique():,}")
    col2.metric("Avg Sessions / Customer", f"{len(df)/df['customer_id'].nunique():.1f}")
    col3.metric("Avg Spend / Customer", f"₹{df.groupby('customer_id')['cost_inr'].sum().mean():,.0f}")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Customer Segments")
        seg = df.drop_duplicates("customer_id")["customer_segment"].value_counts()
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(seg.values, labels=seg.index, autopct="%1.1f%%")
        st.pyplot(fig)
    with c2:
        st.subheader("Customer Type Mix")
        ctype = df.drop_duplicates("customer_id")["customer_type"].value_counts()
        st.bar_chart(ctype)

    st.subheader("Top 10 Customers by Spend")
    top = df.groupby("customer_id")["cost_inr"].sum().sort_values(ascending=False).head(10)
    st.dataframe(top.reset_index().rename(columns={"cost_inr": "total_spend"}))

# ========================================================================
# PAGE 5 — REVENUE & PROFITABILITY
# ========================================================================
elif page == "💰 Revenue & Profitability":
    st.title("Revenue & Profitability")

    station_summary = df.groupby(["station_id", "station_name"]).agg(
        revenue=("cost_inr", "sum"),
        sessions=("session_id", "count"),
        energy_kwh=("energy_consumed_kwh", "sum"),
    ).reset_index().sort_values("revenue", ascending=False)

    # Simple electricity cost estimate for the dashboard (matches generation assumption)
    station_summary["est_electricity_cost"] = station_summary["energy_kwh"] * 1.1 * 8.5
    station_summary["gross_margin"] = station_summary["revenue"] - station_summary["est_electricity_cost"]

    st.dataframe(station_summary, use_container_width=True)

    st.subheader("Gross Margin by Station")
    st.bar_chart(station_summary.set_index("station_name")["gross_margin"])

    st.subheader("Revenue per Charger Type")
    rev_ct = df.groupby("charger_type")["cost_inr"].sum()
    st.bar_chart(rev_ct)
