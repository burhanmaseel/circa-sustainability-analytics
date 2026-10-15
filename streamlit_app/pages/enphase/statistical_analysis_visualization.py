# -*- coding: utf-8 -*-
"""
Statistical analysis visualization for the Enphase 15-min dashboard.
Displays descriptive statistics, correlation matrix, distributions,
and time-based grouped statistics.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


METRIC_LABELS = {
    "energy_produced": "Energy Produced (Wh)",
    "energy_consumed": "Energy Consumed (Wh)",
    "grid_exported": "Exported to Grid (Wh)",
    "grid_imported": "Imported from Grid (Wh)",
}

METRIC_COLORS = {
    "energy_produced": "#2ecc71",
    "energy_consumed": "#3498db",
    "grid_exported": "#e67e22",
    "grid_imported": "#e74c3c",
}


def statistical_analysis_section(data: pd.DataFrame):
    """
    Display statistical analysis section.

    :param data: DataFrame indexed by timestamp with Enphase energy columns
    """
    st.header("Statistical Analysis")

    if data.empty:
        st.warning("No data available for the selected date range.")
        return

    metrics = list(METRIC_LABELS.keys())

    # ── Descriptive Statistics ────────────────────────────────────────────────
    st.subheader("Descriptive Statistics (15-min intervals)")

    stats_df = data[metrics].describe()
    stats_df.columns = [METRIC_LABELS[c] for c in stats_df.columns]
    st.dataframe(stats_df.round(2), use_container_width=True)

    # ── Correlation Matrix ────────────────────────────────────────────────────
    st.subheader("Correlation Matrix")

    corr = data[metrics].corr()
    corr.columns = [METRIC_LABELS[c] for c in corr.columns]
    corr.index = [METRIC_LABELS[c] for c in corr.index]

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        ax=ax,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Correlation Matrix of Energy Metrics", fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # ── Distribution Analysis ─────────────────────────────────────────────────
    st.subheader("Distribution Analysis")

    selected_col = st.selectbox(
        "Select metric for distribution analysis",
        options=metrics,
        format_func=lambda c: METRIC_LABELS[c],
        key="stat_dist_metric",
    )
    color = METRIC_COLORS[selected_col]

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(8, 6))
        data[selected_col].hist(bins=50, alpha=0.75, ax=ax, color=color)
        ax.set_title(f"Distribution of {METRIC_LABELS[selected_col]}", fontsize=11)
        ax.set_xlabel("Wh")
        ax.set_ylabel("Frequency")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(8, 6))
        data[[selected_col]].boxplot(ax=ax, patch_artist=True,
                                     boxprops=dict(facecolor=color, alpha=0.6))
        ax.set_title(f"Box Plot of {METRIC_LABELS[selected_col]}", fontsize=11)
        ax.set_ylabel("Wh")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # ── Time-based Statistics ─────────────────────────────────────────────────
    st.subheader("Time-based Statistics")

    analysis_period = st.selectbox(
        "Select grouping period",
        ["Hourly", "Daily", "Weekly", "Monthly"],
        key="stat_period_select",
    )

    if analysis_period == "Hourly":
        grouped = data.groupby(data.index.hour)[metrics].agg(["mean", "std", "min", "max"])
        grouped.index.name = "Hour"
    elif analysis_period == "Daily":
        grouped = data.groupby(data.index.date)[metrics].agg(["mean", "std", "min", "max"])
        grouped.index.name = "Date"
    elif analysis_period == "Weekly":
        grouped = data.resample("W")[metrics].agg(["mean", "std", "min", "max"])
    else:  # Monthly
        grouped = data.resample("ME")[metrics].agg(["mean", "std", "min", "max"])

    # Rename columns for readability
    grouped.columns = [
        f"{METRIC_LABELS[col]} — {stat}" for col, stat in grouped.columns
    ]
    st.dataframe(grouped.round(2), use_container_width=True)
