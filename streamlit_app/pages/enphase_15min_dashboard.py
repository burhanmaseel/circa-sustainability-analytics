# -*- coding: utf-8 -*-
"""
Enphase 15-Minute Energy Analytics Dashboard
---------------------------------------------
Advanced tab-based dashboard for Enphase 15-min energy data sourced from
the PostgreSQL database (v_enphase view).

Tabs:
  1. Overview         — KPI metrics + daily energy flow subplots
  2. Time Series      — Raw series, seasonal decomposition, rolling stats
  3. Daily Patterns   — Hourly averages, day-of-week bar charts, heatmap
  4. Energy Balance   — Net energy, grid balance, self-consumption analysis
  5. Statistics       — Descriptive stats, correlation, distributions
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# ── Path setup ────────────────────────────────────────────────────────────────
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

from utils.data_reader import (
    get_enphase_15min_data,
    get_enphase_date_range,
    get_artefact_data_stats,
)
from pages.enphase.overview_visualization import overview_section
from pages.enphase.time_series_visualization import time_series_section
from pages.enphase.daily_patterns_visualization import daily_patterns_section
from pages.enphase.energy_balance_visualization import energy_balance_section
from pages.enphase.statistical_analysis_visualization import statistical_analysis_section


@st.cache_data(ttl=300)
def load_data(start_date, end_date):
    """Cached DB fetch for the selected date range."""
    return get_enphase_15min_data(start_date, end_date)


def enphase_15min_dashboard():
    """Advanced 15-minute Enphase analytics dashboard (DB-backed)."""

    st.title("Enphase 15-Minute Energy Analytics Dashboard")

    # ── Data availability banner ──────────────────────────────────────────────
    artefact_stats = get_artefact_data_stats(2)  # artefact_type_id 2 = Enphase

    if not artefact_stats.empty and not pd.isna(artefact_stats["min_ts"].iloc[0]):
        min_ts = artefact_stats["min_ts"].iloc[0]
        max_ts = artefact_stats["max_ts"].iloc[0]
        num_days = int(artefact_stats["num_days"].iloc[0])
        st.write(
            f"Data available from **{min_ts.date()}** to "
            f"**{max_ts.strftime('%Y-%m-%d %H:%M:%S')}** — "
            f"**{num_days}** days"
        )
    else:
        st.error("No Enphase data found in the database.")
        return

    # ── Sidebar controls ──────────────────────────────────────────────────────
    st.sidebar.header("Dashboard Controls")

    min_date, max_date = get_enphase_date_range()
    if min_date is None:
        st.error("Could not determine date range from the database.")
        return

    start_date = st.sidebar.date_input(
        "Start Date", value=min_date, min_value=min_date, max_value=max_date,
        key="eph_start",
    )
    end_date = st.sidebar.date_input(
        "End Date", value=max_date, min_value=min_date, max_value=max_date,
        key="eph_end",
    )

    if start_date > end_date:
        st.sidebar.error("Start date must be before end date.")
        return

    # ── Load data ─────────────────────────────────────────────────────────────
    with st.spinner("Loading Enphase data from database…"):
        data = load_data(start_date, end_date)

    if data.empty:
        st.warning("No data available for the selected date range.")
        return

    record_count = len(data)
    st.sidebar.info(
        f"Loaded **{record_count:,}** records\n"
        f"({start_date} → {end_date})"
    )

    # ── Tab layout ────────────────────────────────────────────────────────────
    tabs = st.tabs(
        ["Overview", "Time Series", "Daily Patterns", "Energy Balance", "Statistics"]
    )

    with tabs[0]:
        overview_section(data)

    with tabs[1]:
        time_series_section(data)

    with tabs[2]:
        daily_patterns_section(data)

    with tabs[3]:
        energy_balance_section(data)

    with tabs[4]:
        statistical_analysis_section(data)


if __name__ == "__main__":
    enphase_15min_dashboard()
