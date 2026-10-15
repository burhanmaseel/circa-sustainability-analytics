# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 16:00:35 2024

@author: vpp
"""

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from pathlib import Path
import sys

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.utils.data_reader import read_enphase_panel_data_file


def solar_panel_dashboard():
    import scipy.stats as stats
    
    # Load the data
    data = read_enphase_panel_data_file(os.path.join(project_root, "data", "sample", "enphase"), 'enphase_daily_Feb23_Sep24_module.csv', True)

    # Group modules by their location (_C, _S, _SE)
    location_groups = {
        "_C": [col for col in data.columns if "_C" in col], # 8 Panels 0 degrees tilt
        "_S": [col for col in data.columns if "_S" in col and "_SE" not in col],  # Ensure _S excludes _SE, 20 panels with 8 degrees tilt
        "_SE": [col for col in data.columns if "_SE" in col],  # 9 Panels with 8 degrees tilt
    }

    # Streamlit app
    st.title("Solar Panel Data Analysis")

    # Date selection
    start_date = st.date_input("Start Date", value=data.index.min().date())
    end_date = st.date_input("End Date", value=data.index.max().date())

    # Module selection
    module_name = st.selectbox("Select Module", data.columns)

    # Filter data for single module
    filtered_data_single = data.loc[start_date:end_date]

    # Single module plot
    st.subheader(f"Data for {module_name}")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(filtered_data_single.index, filtered_data_single[module_name], marker='o', label=module_name)
    ax.set_title(f"Data for {module_name}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Wh")
    ax.legend()
    st.pyplot(fig)

    # Group selection
    group_selection = st.selectbox("Select Location Group", list(location_groups.keys()))
    selected_columns = location_groups[group_selection]

    # Filter data for group
    filtered_data_group = data.loc[start_date:end_date, selected_columns]

    # Grouped plot
    st.subheader(f"Data for Location Group: {group_selection}")
    fig, ax = plt.subplots(figsize=(12, 8))
    for column in selected_columns:
        ax.plot(filtered_data_group.index, filtered_data_group[column], label=column)
    ax.set_title(f"Production Data for Group {group_selection}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Wh")
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # Move legend outside the plot
    st.pyplot(fig)

    # ANOVA Test
    st.subheader("ANOVA Test for Grouped Data")
    if len(selected_columns) > 1:
        anova_result = stats.f_oneway(*[filtered_data_group[col].dropna() for col in selected_columns])
        st.write(f"F-statistic: {anova_result.statistic:.2f}, p-value: {anova_result.pvalue:.5f}")
        if anova_result.pvalue < 0.05:
            st.warning("Significant difference detected in production across the selected group.")
        else:
            st.success("No significant difference in production between panels in this group.")

    # Time Series Decomposition
    st.subheader("Time Series Decomposition")
    ts_module_name = st.selectbox("Select Module for Time Series Analysis", data.columns, key="ts_module")
    ts_filtered_data = data.loc[start_date:end_date, ts_module_name]

    # Select period dynamically
    seasonality_option = st.selectbox("Select Seasonality Period", options=["Weekly (7)", "Monthly (30)", "Yearly (365)"])
    period = int(seasonality_option.split('(')[1].split(')')[0])

    data_length = len(ts_filtered_data)
    if data_length >= 2 * period:
        decomposition = seasonal_decompose(ts_filtered_data, model='additive', period=period)

        fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
        decomposition.observed.plot(ax=axes[0], title='Observed')
        decomposition.trend.plot(ax=axes[1], title='Trend')
        decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
        decomposition.resid.plot(ax=axes[3], title='Residual')
        plt.xlabel("Date")
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning(f"Not enough data points for time series decomposition with period = {period}. Try selecting a longer date range.")

    # Statistics
    st.subheader("Statistics")
    stats_start_date = st.date_input("Statistics Start Date", value=data.index.min().date(), key="stats_start")
    stats_end_date = st.date_input("Statistics End Date", value=data.index.max().date(), key="stats_end")
    stats_selection_type = st.radio("Select Statistics Type", ("Single Module", "Group"), key="stats_type")

    if stats_selection_type == "Single Module":
        stats_module_name = st.selectbox("Select Module for Statistics", data.columns, key="stats_module")
        stats_filtered_data = data.loc[stats_start_date:stats_end_date, stats_module_name]
        stats = {
            "Min": stats_filtered_data.min(),
            "Max": stats_filtered_data.max(),
            "Average": stats_filtered_data.mean(),
            "Standard Deviation": stats_filtered_data.std(),
            "Sum": stats_filtered_data.sum()
        }
        st.write(pd.DataFrame(stats, index=[stats_module_name]))
    else:
        stats_group_selection = st.selectbox("Select Location Group for Statistics", list(location_groups.keys()), key="stats_group")
        stats_columns = location_groups[stats_group_selection]
        stats_filtered_data = data.loc[stats_start_date:stats_end_date, stats_columns]
        stats = stats_filtered_data.describe().T
        stats['Sum'] = stats_filtered_data.sum()
        total_sum = stats_filtered_data.sum(axis=1).sum()
        st.write(stats)
        st.write(f"**Total Sum for {stats_group_selection}: {total_sum:.2f} Wh**")


