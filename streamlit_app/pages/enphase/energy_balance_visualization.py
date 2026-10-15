# -*- coding: utf-8 -*-
"""
Energy balance visualization for the Enphase 15-min dashboard.
Displays net energy, grid balance, self-consumption rate, and balance statistics.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def energy_balance_section(data: pd.DataFrame):
    """
    Display energy balance analysis: net energy, grid balance, self-consumption.

    :param data: DataFrame indexed by timestamp with Enphase energy columns
    """
    st.header("Energy Balance Analysis")

    if data.empty:
        st.warning("No data available for the selected date range.")
        return

    # ── Daily Aggregation ─────────────────────────────────────────────────────
    daily = data.resample("D").sum()
    daily["Net_Energy"] = daily["energy_produced"] - daily["energy_consumed"]
    daily["Grid_Balance"] = daily["grid_exported"] - daily["grid_imported"]
    daily["Self_Consumption"] = daily["energy_produced"] - daily["grid_exported"]
    daily["Self_Consumption_Rate"] = (
        daily["Self_Consumption"] / daily["energy_produced"].replace(0, float("nan")) * 100
    ).fillna(0)

    # ── Charts ────────────────────────────────────────────────────────────────
    st.subheader("Daily Energy Balance")

    fig, axes = plt.subplots(3, 1, figsize=(15, 13))

    # Net energy (Produced − Consumed)
    net_colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in daily["Net_Energy"]]
    axes[0].bar(daily.index, daily["Net_Energy"], color=net_colors, alpha=0.78, width=0.8)
    axes[0].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[0].set_title("Daily Net Energy Balance (Produced − Consumed)", fontsize=12)
    axes[0].set_ylabel("Net Energy (Wh)")
    axes[0].grid(True, alpha=0.3)

    # Grid balance (Exported − Imported)
    grid_colors = ["#e67e22" if v >= 0 else "#3498db" for v in daily["Grid_Balance"]]
    axes[1].bar(daily.index, daily["Grid_Balance"], color=grid_colors, alpha=0.78, width=0.8)
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[1].set_title("Daily Grid Balance (Exported − Imported)", fontsize=12)
    axes[1].set_ylabel("Grid Balance (Wh)")
    axes[1].grid(True, alpha=0.3)

    # Self-consumption rate
    axes[2].plot(
        daily.index,
        daily["Self_Consumption_Rate"],
        marker="o",
        color="#8e44ad",
        linewidth=2,
        markersize=3,
    )
    axes[2].set_title("Daily Self-Consumption Rate", fontsize=12)
    axes[2].set_ylabel("Self-Consumption (%)")
    axes[2].set_xlabel("Date")
    axes[2].grid(True, alpha=0.3)

    for ax in axes:
        ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # ── Statistics ────────────────────────────────────────────────────────────
    st.subheader("Energy Balance Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Daily Averages:**")
        avg_stats = daily[
            [
                "energy_produced",
                "energy_consumed",
                "grid_exported",
                "grid_imported",
                "Net_Energy",
                "Grid_Balance",
                "Self_Consumption_Rate",
            ]
        ].mean().rename({
            "energy_produced": "Energy Produced (Wh)",
            "energy_consumed": "Energy Consumed (Wh)",
            "grid_exported": "Exported to Grid (Wh)",
            "grid_imported": "Imported from Grid (Wh)",
            "Net_Energy": "Net Energy (Wh)",
            "Grid_Balance": "Grid Balance (Wh)",
            "Self_Consumption_Rate": "Self-Consumption Rate (%)",
        })
        st.dataframe(avg_stats.round(2).to_frame("Average"), use_container_width=True)

    with col2:
        st.write("**Monthly Totals:**")
        monthly = data.resample("ME").sum()
        monthly.index = monthly.index.strftime("%Y-%m")
        monthly = monthly.rename(columns={
            "energy_produced": "Energy Produced (Wh)",
            "energy_consumed": "Energy Consumed (Wh)",
            "grid_exported": "Exported to Grid (Wh)",
            "grid_imported": "Imported from Grid (Wh)",
        })
        monthly["Self-Consumption Rate (%)"] = (
            (monthly["Energy Produced (Wh)"] - monthly["Exported to Grid (Wh)"])
            / monthly["Energy Produced (Wh)"].replace(0, float("nan"))
            * 100
        ).fillna(0)
        st.dataframe(monthly.round(0), use_container_width=True)
