# -*- coding: utf-8 -*-
"""
Time series visualization for the Enphase 15-min dashboard.
Displays raw time series, seasonal decomposition, and rolling statistics.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose


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


def time_series_section(data: pd.DataFrame):
    """
    Display time series analysis: raw plot, seasonal decomposition, rolling stats.

    :param data: DataFrame indexed by timestamp with Enphase energy columns
    """
    st.header("Time Series Analysis")

    if data.empty:
        st.warning("No data available for the selected date range.")
        return

    metrics = list(METRIC_LABELS.keys())
    selected_col = st.selectbox(
        "Select Energy Metric",
        options=metrics,
        format_func=lambda c: METRIC_LABELS[c],
        key="ts_metric_select",
    )
    color = METRIC_COLORS[selected_col]

    # ── Raw Time Series ───────────────────────────────────────────────────────
    st.subheader("Raw 15-Min Time Series")
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(
        data.index,
        data[selected_col],
        color=color,
        linewidth=0.6,
        alpha=0.8,
    )
    ax.set_title(f"{METRIC_LABELS[selected_col]} Over Time", fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("Wh")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # ── Seasonal Decomposition ────────────────────────────────────────────────
    st.subheader("Seasonal Decomposition")

    period_options = {
        "Daily (96 intervals — 15-min data)": 96,
        "Weekly (672 intervals)": 672,
    }
    period_label = st.selectbox(
        "Select Decomposition Period",
        list(period_options.keys()),
        key="ts_period_select",
    )
    period = period_options[period_label]

    series = data[selected_col].dropna()

    if len(series) >= 2 * period:
        if len(series) > 10000:
            series = series.iloc[-10000:]
            st.info("Using last 10,000 data points for decomposition (large dataset).")

        try:
            decomposition = seasonal_decompose(series, model="additive", period=period)

            fig, axes = plt.subplots(4, 1, figsize=(15, 12), sharex=True)
            decomposition.observed.plot(ax=axes[0], title="Observed", color=color)
            decomposition.trend.plot(ax=axes[1], title="Trend", color="#8e44ad")
            decomposition.seasonal.plot(ax=axes[2], title="Seasonal", color="#16a085")
            decomposition.resid.plot(ax=axes[3], title="Residual", color="#7f8c8d")
            for ax in axes:
                ax.grid(True, alpha=0.3)
            axes[-1].set_xlabel("Date")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.error(f"Decomposition failed: {e}")
    else:
        st.warning(
            f"Not enough data for decomposition (need ≥ {2 * period} points, "
            f"have {len(series)}). Try a wider date range or Daily period."
        )

    # ── Rolling Statistics ────────────────────────────────────────────────────
    st.subheader("Rolling Statistics")

    window_hours = st.slider(
        "Rolling Window Size (hours)", min_value=1, max_value=24, value=6,
        key="ts_window_slider",
    )
    window = window_hours * 4  # Convert hours → 15-min intervals

    series_full = data[selected_col]
    rolling_mean = series_full.rolling(window=window).mean()
    rolling_std = series_full.rolling(window=window).std()

    fig, axes = plt.subplots(2, 1, figsize=(15, 8))

    axes[0].plot(series_full.index, series_full, alpha=0.3, label="Original", color=color)
    axes[0].plot(
        rolling_mean.index, rolling_mean,
        label=f"Rolling Mean ({window_hours}h)", color="#c0392b", linewidth=1.5
    )
    axes[0].set_title(f"Rolling Mean — {METRIC_LABELS[selected_col]}")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(
        rolling_std.index, rolling_std,
        label=f"Rolling Std ({window_hours}h)", color="#e67e22", linewidth=1.5
    )
    axes[1].set_title(f"Rolling Std Deviation — {METRIC_LABELS[selected_col]}")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
