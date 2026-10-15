import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from utils.weather_data import calculate_temperature_stats, handle_missing_data, create_time_series_chart
from utils.data_reader import get_open_weather_temperature_data

def temperature_section():
    """
    Display temperature section in the weather dashboard
    """
    st.write("### Temperature Analysis")
    
    weather_data = get_open_weather_temperature_data()

    if weather_data.empty:
        st.write("No data available in DB for Temperature.")
        return

    weather_data['ts'] = pd.to_datetime(weather_data['ts'])
    weather_data.set_index('ts', inplace=True)


    
    # Handle missing data
    weather_data = handle_missing_data(weather_data, 'temp')
    weather_data = handle_missing_data(weather_data, 'feels_like')
    weather_data = handle_missing_data(weather_data, 'temp_min')
    weather_data = handle_missing_data(weather_data, 'temp_max')
    
    # Temperature statistics
    st.write("#### Temperature Statistics")
    temp_stats = calculate_temperature_stats(weather_data, 'temp')
    st.write(temp_stats)
    
    # Temperature time series
    st.write("#### Temperature Over Time")
    temp_fig = create_time_series_chart(
        weather_data, 
        'temp', 
        'Temperature Over Time', 
        'Temperature (°K)', 
        color='red'
    )
    st.pyplot(temp_fig)
    
    # Temperature vs Feels Like
    if 'feels_like' in weather_data.columns:
        st.write("#### Temperature vs. Feels Like")
        fig, ax = plt.subplots(figsize=(12, 6))
        weather_data['temp'].plot(ax=ax, label='Actual Temperature', color='red', alpha=0.7)
        weather_data['feels_like'].plot(ax=ax, label='Feels Like', color='orange', alpha=0.7)
        ax.set_title("Actual Temperature vs. Feels Like")
        ax.set_xlabel("Date")
        ax.set_ylabel("Temperature (°K)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    # Min-Max Temperature Range
    if 'temp_min' in weather_data.columns and 'temp_max' in weather_data.columns:
        st.write("#### Daily Temperature Range")
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create a sample of data points to avoid overcrowding the chart
        sample_size = min(100, len(weather_data))
        sampled_data = weather_data.sample(sample_size) if len(weather_data) > sample_size else weather_data
        
        # Sort by date for better visualization
        sampled_data = sampled_data.sort_index()
        
        # Plot temperature range
        for idx, row in sampled_data.iterrows():
            ax.vlines(x=idx, ymin=row['temp_min'], ymax=row['temp_max'], color='blue', alpha=0.5)
        
        sampled_data['temp'].plot(ax=ax, color='red', marker='o', linestyle='', alpha=0.7, label='Actual Temp')
        
        ax.set_title("Temperature Range (Min-Max)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Temperature (°K)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    # Temperature distribution
    st.write("#### Temperature Distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    weather_data['temp'].hist(bins=20, ax=ax, color='red', alpha=0.7)
    ax.set_title("Temperature Distribution")
    ax.set_xlabel("Temperature (°K)")
    ax.set_ylabel("Frequency")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
