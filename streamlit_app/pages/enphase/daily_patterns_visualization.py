# -*- coding: utf-8 -*-
"""
Daily patterns visualization for the Enphase 15-min dashboard.
Displays average hourly profiles, day-of-week bar charts, and a heatmap.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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

DAY_ORDER = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]


def daily_patterns_section(data: pd.DataFrame):
    """
    Display daily pattern analysis.

    :param data: DataFrame indexed by timestamp with Enphase energy columns
    """
    st.header("Daily Energy Patterns")

    if data.empty:
        st.warning("No data available for the selected date range.")
        return

    metrics = list(METRIC_LABELS.keys())
    colors = [METRIC_COLORS[m] for m in metrics]

    # ── Average Hourly Patterns ───────────────────────────────────────────────
    st.subheader("Average Hourly Profiles (15-min interval averaged)")

    data_copy = data.copy()
    data_copy["Hour"] = data_copy.index.hour

    hourly_avg = data_copy.groupby("Hour")[metrics].mean()

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()

    for i, (metric, color) in enumerate(zip(metrics, colors)):
        axes[i].plot(
            hourly_avg.index,
            hourly_avg[metric],
            marker="o",
            color=color,
            linewidth=2,
            markersize=4,
        )
        axes[i].set_title(f"Avg {METRIC_LABELS[metric]}", fontsize=11)
        axes[i].set_xlabel("Hour of Day")
        axes[i].set_ylabel("Wh")
        axes[i].set_xlim(0, 23)
        axes[i].grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # ── Day of Week Patterns ──────────────────────────────────────────────────
    st.subheader("Average Energy by Day of Week")

    data_copy["Day_of_Week"] = data_copy.index.day_name()
    dow_avg = data_copy.groupby("Day_of_Week")[metrics].mean().reindex(DAY_ORDER)

    fig, ax = plt.subplots(figsize=(13, 6))
    x = np.arange(len(DAY_ORDER))
    width = 0.2

    for i, (metric, color) in enumerate(zip(metrics, colors)):
        ax.bar(
            x + i * width,
            dow_avg[metric],
            width,
            label=METRIC_LABELS[metric].replace(" (Wh)", ""),
            color=color,
            alpha=0.75,
        )

    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Average Energy (Wh)")
    ax.set_title("Average Energy by Day of Week")
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(DAY_ORDER)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # ── Heatmap: Hour vs Day of Week ──────────────────────────────────────────
    st.subheader("Energy Production Heatmap (Hour × Day of Week)")

    heatmap_data = data_copy.pivot_table(
        values="energy_produced",
        index="Hour",
        columns="Day_of_Week",
        aggfunc="mean",
    ).reindex(columns=DAY_ORDER)

    fig, ax = plt.subplots(figsize=(11, 8))
    sns.heatmap(
        heatmap_data,
        annot=False,
        cmap="YlOrRd",
        ax=ax,
        cbar_kws={"label": "Avg Energy Produced (Wh)"},
        linewidths=0.3,
    )
    ax.set_title("Average Energy Production by Hour and Day of Week", fontsize=13)
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Hour of Day")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
