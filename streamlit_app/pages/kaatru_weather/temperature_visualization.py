import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from utils.weather_data import calculate_temperature_stats, handle_missing_data, create_time_series_chart
from utils.data_reader import get_artefact_attributes_data

def temperature_section():
    """
    Display Temperature section.
    """
    st.write("### Temperature Analysis")

    artefact_type_attributes = ('value.temp',)
    results = get_artefact_attributes_data(artefact_type_attributes)

    if results.empty:
        st.write("No data available in DB for Temperature.")
        return

    # Pivot data
    chart_data = results.copy()
    chart_data['ts'] = pd.to_datetime(chart_data['ts'])
    chart_data['numeric_value'] = pd.to_numeric(chart_data['numeric_value'], errors='coerce')
    data = chart_data.pivot(index='ts', columns='attribute_name', values='numeric_value')

    if 'value.temp' not in data.columns:
        st.write("No Temperature attribute found in data.")
        return

    # Handle missing data
    data = handle_missing_data(data, 'value.temp')

    # Temperature statistics
    st.write("#### Temperature Statistics")
    temp_stats = calculate_temperature_stats(data, 'value.temp')
    st.write(temp_stats)

    # Temperature time series
    st.write("#### Temperature Over Time")
    temp_fig = create_time_series_chart(
        data,
        'value.temp',
        'Temperature Over Time',
        'Temperature',
        color='red'
    )
    st.pyplot(temp_fig)

    # Temperature distribution
    st.write("#### Temperature Distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    data['value.temp'].hist(bins=20, ax=ax, color='red', alpha=0.7)
    ax.set_title("Temperature Distribution")
    ax.set_xlabel("Temperature")
    ax.set_ylabel("Frequency")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
