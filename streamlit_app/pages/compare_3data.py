import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import pvlib
import numpy as np
from pathlib import Path
import sys
import os

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.utils.data_reader import read_enphase_panel_data_file, read_solar_data_file


def comparison_tables():
    # --- Load actual data (from module file) ---

    enphase_directory = os.path.join(project_root, "data", "sample", "enphase")
    actual_df = read_enphase_panel_data_file(enphase_directory, 'Feb23_Sep24_module.csv', True)

    # Convert month names to numbers and convert to datetime
    actual_df['Month'] = pd.to_datetime(actual_df['Month'], format='%B').dt.month
    actual_df['Date'] = pd.to_datetime(actual_df[['Year', 'Month', 'Day']])
    actual_df.set_index('Date', inplace=True)

    # Convert Wh to kWh (excluding non-numeric columns)
    exclude_cols = ['Total', 'Month', 'Day', 'Year']
    cols_to_convert = actual_df.columns.difference(exclude_cols)

    # Clean and convert numeric columns
    actual_df[cols_to_convert] = (actual_df[cols_to_convert]
                                .replace({',': ''}, regex=True)  # Remove commas
                                .apply(pd.to_numeric, errors='coerce') / 1000)  # Convert to kWh

    # Setup groupings
    setup_map = {
        "Setup 1": [col for col in actual_df.columns if "_S" in col and "_SE" not in col],
        "Setup 2": [col for col in actual_df.columns if "_C" in col],
        "Setup 3": [col for col in actual_df.columns if "_SE" in col]
    }

    # Aggregate actual data for each setup
    actual_aggregated = {setup: actual_df[cols].sum(axis=1) for setup, cols in setup_map.items()}

    # Convert to DataFrame
    actual_aggregated_df = pd.DataFrame(actual_aggregated)

    # --- Load predicted data from weather ---
    predicted_df = read_solar_data_file("predicted_solar_output.csv")
    predicted_df.columns = predicted_df.columns.str.strip()
    predicted_df.rename(columns=lambda x: x.strip('"'), inplace=True)
    predicted_df['Date'] = pd.to_datetime(predicted_df['Date'])

    # Predicted column mapping
    pred_col_map = {"Setup 1": "Setup 1", "Setup 2": "Setup 2", "Setup 3": "Setup 3"}

    # Aggregate predicted data using number of panels
    panel_counts = {"Setup 1": 20, "Setup 2": 8, "Setup 3": 9}
    for setup, col in pred_col_map.items():
        predicted_df[col] = predicted_df[col] * panel_counts[setup]

    # --- Load NASA (clear-sky) output ---
    nasa_df = read_solar_data_file("solar_output.csv")
    nasa_df.columns = nasa_df.columns.str.strip()
    nasa_df.rename(columns=lambda x: x.strip('"'), inplace=True)
    nasa_df['Date'] = pd.to_datetime(nasa_df['Date'])

    # NASA column mapping
    nasa_col_map = {"Setup 1": "Setup 1", "Setup 2": "Setup 2", "Setup 3": "Setup 3"}

    # Aggregate NASA data using number of panels
    for setup, col in nasa_col_map.items():
        nasa_df[col] = nasa_df[col] * panel_counts[setup]

    # Streamlit UI
    st.title("Comparison of Actual, Weather-based, and NASA-based Solar Output")
    setup_option = st.selectbox("Select Setup", ["Setup 1", "Setup 2", "Setup 3"])
    date_range = st.date_input("Select Date Range", [actual_df.index.min().date(), actual_df.index.max().date()])

    # Filter actual
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    actual_filtered = actual_aggregated_df.loc[start_date:end_date, setup_option].reset_index(name="Actual")

    # Merge predicted and NASA data
    merged = actual_filtered.merge(predicted_df[['Date', pred_col_map[setup_option]]], on='Date', how='inner')
    merged = merged.merge(nasa_df[['Date', nasa_col_map[setup_option]]], on='Date', how='inner')

    # Rename columns
    merged.columns = ['Date', 'Actual', 'Predicted (Weather)', 'Predicted (NASA Clear Sky)']
    merged.set_index('Date', inplace=True)

    # Plotting
    st.subheader(f"Comparison of Solar Output for {setup_option}")
    fig, ax = plt.subplots(figsize=(12, 6))
    merged.plot(ax=ax, marker='o')
    ax.set_ylabel("Solar Output (kWh)")
    ax.set_xlabel("Date")
    ax.set_title(f"Actual vs Predicted Solar Output - {setup_option}")
    ax.grid(True)
    st.pyplot(fig)

    # Show table
    st.subheader("Comparison Table")
    st.dataframe(merged.round(2))