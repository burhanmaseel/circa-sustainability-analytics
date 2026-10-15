# -*- coding: utf-8 -*-
"""
Enphase 15-Minute Simple Dashboard
-----------------------------------
All-panels-combined daily energy analytics sourced from the PostgreSQL database
(v_enphase view).  Preserves all legacy analytics:
  - Time series plot per metric
  - All-metrics comparison plot
  - Daily totals bar charts (2×2)
  - Average hourly patterns (2×2)
  - Energy balance analysis (Net Energy, Grid Balance, Self Consumption)
  - Time series decomposition
  - Descriptive statistics + energy balance summary metrics
"""

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from pathlib import Path
import sys

# ── Path setup ────────────────────────────────────────────────────────────────
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

from utils.data_reader import get_enphase_15min_data, get_enphase_date_range

# ── Constants ─────────────────────────────────────────────────────────────────
# DB column → friendly label mapping (preserves original display names)
METRIC_LABELS = {
    "energy_produced": "Energy Produced (Wh)",
    "energy_consumed": "Energy Consumed (Wh)",
    "grid_exported": "Exported to Grid (Wh)",
    "grid_imported": "Imported from Grid (Wh)",
}
METRICS = list(METRIC_LABELS.keys())
COLORS = ["green", "blue", "orange", "red"]


@st.cache_data(ttl=300)
def load_data(start_date, end_date):
    """Cached DB fetch for the selected date range."""
    return get_enphase_15min_data(start_date, end_date)


def enphase_15min_simple_dashboard():
    """Simple dashboard for 15-minute Enphase energy data (DB-backed)."""

    st.title("Enphase 15-Minute Energy Data Analysis")

    # ── Date range from DB ────────────────────────────────────────────────────
    min_date, max_date = get_enphase_date_range()

    if min_date is None:
        st.error("No Enphase data found in the database.")
        return

    st.write(
        f"Data available from **{min_date}** to **{max_date}**"
    )

    # ── Date selection ────────────────────────────────────────────────────────
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input(
            "Start Date", value=min_date, min_value=min_date, max_value=max_date
        )
    with col_d2:
        end_date = st.date_input(
            "End Date", value=max_date, min_value=min_date, max_value=max_date
        )

    if start_date > end_date:
        st.error("Start date must be before or equal to end date.")
        return

    # ── Load filtered data ────────────────────────────────────────────────────
    with st.spinner("Loading data…"):
        data = load_data(start_date, end_date)

    if data.empty:
        st.warning("No data available for the selected date range.")
        return

    # ── Metric selection ──────────────────────────────────────────────────────
    metric_col = st.selectbox(
        "Select Energy Metric",
        options=METRICS,
        format_func=lambda c: METRIC_LABELS[c],
    )

    # ── Single metric time series ─────────────────────────────────────────────
    st.subheader(f"Time Series: {METRIC_LABELS[metric_col]}")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(data.index, data[metric_col], linewidth=0.8, alpha=0.75, color="steelblue")
    ax.set_title(f"{METRIC_LABELS[metric_col]} Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Wh")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # ── All metrics comparison ────────────────────────────────────────────────
    st.subheader("All Energy Metrics Comparison")
    fig, ax = plt.subplots(figsize=(14, 6))
    for metric, color in zip(METRICS, COLORS):
        ax.plot(
            data.index,
            data[metric],
            label=METRIC_LABELS[metric].replace(" (Wh)", ""),
            color=color,
            alpha=0.8,
            linewidth=1.2,
        )
    ax.set_title("Energy Metrics Comparison")
    ax.set_xlabel("Date")
    ax.set_ylabel("Energy (Wh)")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # ── Daily aggregation ─────────────────────────────────────────────────────
    st.subheader("Daily Energy Analysis")

    daily_data = data.resample("D").sum()

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()

    for i, (metric, color) in enumerate(zip(METRICS, COLORS)):
        axes[i].bar(
            daily_data.index, daily_data[metric],
            color=color, alpha=0.72, width=0.8,
        )
        axes[i].set_title(f"Daily {METRIC_LABELS[metric].replace(' (Wh)', '')}")
        axes[i].set_xlabel("Date")
        axes[i].set_ylabel("Wh")
        axes[i].grid(True, alpha=0.3)
        axes[i].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # ── Hourly patterns ───────────────────────────────────────────────────────
    st.subheader("Average Hourly Patterns")

    data_h = data.copy()
    data_h["Hour"] = data_h.index.hour
    hourly_avg = data_h.groupby("Hour")[METRICS].mean()

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()

    for i, (metric, color) in enumerate(zip(METRICS, COLORS)):
        axes[i].plot(
            hourly_avg.index, hourly_avg[metric],
            marker="o", color=color, linewidth=2, markersize=4,
        )
        axes[i].set_title(f"Average Hourly {METRIC_LABELS[metric].replace(' (Wh)', '')}")
        axes[i].set_xlabel("Hour of Day")
        axes[i].set_ylabel("Wh")
        axes[i].grid(True, alpha=0.3)
        axes[i].set_xlim(0, 23)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # ── Energy balance analysis ───────────────────────────────────────────────
    st.subheader("Energy Balance Analysis")

    db = daily_data.copy()
    db["Net_Energy"] = db["energy_produced"] - db["energy_consumed"]
    db["Grid_Balance"] = db["grid_exported"] - db["grid_imported"]
    db["Self_Consumption"] = db["energy_produced"] - db["grid_exported"]

    fig, axes = plt.subplots(3, 1, figsize=(14, 12))

    # Net energy
    net_colors = ["green" if v >= 0 else "red" for v in db["Net_Energy"]]
    axes[0].bar(db.index, db["Net_Energy"], color=net_colors, alpha=0.72, width=0.8)
    axes[0].set_title("Daily Net Energy Balance (Production − Consumption)")
    axes[0].set_ylabel("Net Energy (Wh)")
    axes[0].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[0].grid(True, alpha=0.3)

    # Grid balance
    grid_colors = ["orange" if v >= 0 else "blue" for v in db["Grid_Balance"]]
    axes[1].bar(db.index, db["Grid_Balance"], color=grid_colors, alpha=0.72, width=0.8)
    axes[1].set_title("Daily Grid Balance (Export − Import)")
    axes[1].set_ylabel("Grid Balance (Wh)")
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[1].grid(True, alpha=0.3)

    # Self consumption
    axes[2].bar(db.index, db["Self_Consumption"], color="purple", alpha=0.72, width=0.8)
    axes[2].set_title("Daily Self Consumption")
    axes[2].set_ylabel("Self Consumption (Wh)")
    axes[2].set_xlabel("Date")
    axes[2].grid(True, alpha=0.3)

    for ax in axes:
        ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # ── Time series decomposition ─────────────────────────────────────────────
    st.subheader("Time Series Decomposition")

    ts_col = st.selectbox(
        "Select Metric for Time Series Analysis",
        options=METRICS,
        format_func=lambda c: METRIC_LABELS[c],
        key="ts_decomp_metric",
    )
    seasonality_option = st.selectbox(
        "Select Seasonality Period",
        options=["Daily (96 intervals)", "Weekly (672 intervals)"],
    )
    period = 96 if "Daily" in seasonality_option else 672

    ts_series = data[ts_col].dropna()
    if len(ts_series) >= 2 * period:
        if len(ts_series) > 5000:
            ts_series = ts_series.iloc[-5000:]
            st.info("Using last 5,000 data points for decomposition.")

        decomposition = seasonal_decompose(ts_series, model="additive", period=period)

        fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
        decomposition.observed.plot(ax=axes[0], title="Observed")
        decomposition.trend.plot(ax=axes[1], title="Trend")
        decomposition.seasonal.plot(ax=axes[2], title="Seasonal")
        decomposition.resid.plot(ax=axes[3], title="Residual")
        plt.xlabel("Date")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.warning(
            f"Not enough data for decomposition with period = {period}. "
            "Try a longer date range or choose 'Daily'."
        )

    # ── Statistics summary ────────────────────────────────────────────────────
    st.subheader("Energy Statistics Summary")

    stats_df = data[METRICS].describe()
    stats_df.columns = [METRIC_LABELS[c] for c in stats_df.columns]
    st.write("**Descriptive Statistics for Selected Period:**")
    st.dataframe(stats_df.round(2), use_container_width=True)

    st.write("**Total Energy Summary:**")
    totals = data[METRICS].sum()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Produced", f"{totals['energy_produced']:,.0f} Wh")
    with col2:
        st.metric("Total Consumed", f"{totals['energy_consumed']:,.0f} Wh")
    with col3:
        st.metric("Total Exported", f"{totals['grid_exported']:,.0f} Wh")
    with col4:
        st.metric("Total Imported", f"{totals['grid_imported']:,.0f} Wh")

    net_energy = totals["energy_produced"] - totals["energy_consumed"]
    grid_balance = totals["grid_exported"] - totals["grid_imported"]
    self_consumption = totals["energy_produced"] - totals["grid_exported"]
    self_consumption_rate = (
        (self_consumption / totals["energy_produced"] * 100)
        if totals["energy_produced"] > 0
        else 0
    )

    st.write("**Energy Balance Summary:**")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Net Energy",
            f"{net_energy:,.0f} Wh",
            "Surplus" if net_energy >= 0 else "Deficit",
        )
    with col2:
        st.metric(
            "Grid Balance",
            f"{grid_balance:,.0f} Wh",
            "Net Export" if grid_balance >= 0 else "Net Import",
        )
    with col3:
        st.metric("Self Consumption", f"{self_consumption:,.0f} Wh")
    with col4:
        st.metric("Self Consumption Rate", f"{self_consumption_rate:.1f}%")


if __name__ == "__main__":
    enphase_15min_simple_dashboard()
