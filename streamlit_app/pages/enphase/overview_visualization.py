# -*- coding: utf-8 -*-
"""
Overview visualization for the Enphase 15-min dashboard.
Displays key KPI metrics and daily energy flow subplots.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Friendly display labels for DB column names
METRIC_LABELS = {
    "energy_produced": "Energy Produced",
    "energy_consumed": "Energy Consumed",
    "grid_exported": "Exported to Grid",
    "grid_imported": "Imported from Grid",
}

METRIC_COLORS = {
    "energy_produced": "#2ecc71",
    "energy_consumed": "#3498db",
    "grid_exported": "#e67e22",
    "grid_imported": "#e74c3c",
}


def overview_section(data: pd.DataFrame):
    """
    Display the overview section: KPI cards + daily energy flow subplots.

    :param data: DataFrame indexed by timestamp with columns
                 energy_produced, energy_consumed, grid_exported, grid_imported
    """
    st.header("Energy System Overview")

    if data.empty:
        st.warning("No data available for the selected date range.")
        return

    # ── KPI Metrics ──────────────────────────────────────────────────────────
    total_produced = data["energy_produced"].sum()
    total_consumed = data["energy_consumed"].sum()
    total_exported = data["grid_exported"].sum()
    total_imported = data["grid_imported"].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Energy Produced",
            f"{total_produced:,.0f} Wh",
            f"{total_produced / 1000:.1f} kWh",
        )
    with col2:
        st.metric(
            "Total Energy Consumed",
            f"{total_consumed:,.0f} Wh",
            f"{total_consumed / 1000:.1f} kWh",
        )
    with col3:
        st.metric(
            "Total Exported to Grid",
            f"{total_exported:,.0f} Wh",
            f"{total_exported / 1000:.1f} kWh",
        )
    with col4:
        st.metric(
            "Total Imported from Grid",
            f"{total_imported:,.0f} Wh",
            f"{total_imported / 1000:.1f} kWh",
        )

    # ── Energy Balance KPIs ───────────────────────────────────────────────────
    st.subheader("Energy Balance Metrics")
    col1, col2, col3 = st.columns(3)

    net_energy = total_produced - total_consumed
    self_consumption = total_produced - total_exported
    self_consumption_rate = (
        (self_consumption / total_produced * 100) if total_produced > 0 else 0
    )
    grid_balance = total_exported - total_imported

    with col1:
        st.metric(
            "Net Energy Balance",
            f"{net_energy:,.0f} Wh",
            "Surplus" if net_energy >= 0 else "Deficit",
        )
    with col2:
        st.metric(
            "Self Consumption",
            f"{self_consumption:,.0f} Wh",
            f"{self_consumption_rate:.1f}%",
        )
    with col3:
        st.metric(
            "Grid Balance",
            f"{grid_balance:,.0f} Wh",
            "Net Export" if grid_balance >= 0 else "Net Import",
        )

    # ── Daily Aggregation ─────────────────────────────────────────────────────
    st.subheader("Daily Energy Flow")

    daily = data.resample("D").sum()

    if daily.empty:
        st.warning("Could not aggregate daily data.")
        return

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Energy Produced (Wh)",
            "Energy Consumed (Wh)",
            "Exported to Grid (Wh)",
            "Imported from Grid (Wh)",
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    traces = [
        ("energy_produced", 1, 1),
        ("energy_consumed", 1, 2),
        ("grid_exported", 2, 1),
        ("grid_imported", 2, 2),
    ]

    for col_name, row, col in traces:
        fig.add_trace(
            go.Scatter(
                x=daily.index,
                y=daily[col_name],
                name=METRIC_LABELS[col_name],
                line=dict(color=METRIC_COLORS[col_name], width=2),
                hovertemplate="%{y:,.0f} Wh<br>%{x|%d %b %Y}<extra></extra>",
            ),
            row=row,
            col=col,
        )

    fig.update_layout(
        height=520,
        showlegend=False,
        title_text="Daily Energy Metrics",
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    fig.update_yaxes(ticksuffix=" Wh")

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Daily Summary Table"):
        display = daily.copy()
        display.index = display.index.strftime("%Y-%m-%d")
        display.columns = [METRIC_LABELS[c] for c in display.columns]
        st.dataframe(display.round(0), use_container_width=True)
