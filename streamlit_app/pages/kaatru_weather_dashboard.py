import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'src'))

from utils.data_reader import get_artefact_data_stats

from pages.kaatru_weather.temperature_visualization import temperature_section
from pages.kaatru_weather.relative_humidity_visualization import relative_humidity_section
from pages.kaatru_weather.wind_speed_visualization import wind_speed_section
from pages.kaatru_weather.rain_visualization import rain_section
from pages.kaatru_weather.pm_visualization import pm_section
from pages.kaatru_weather.npm_number_visualization import npm_number_section
from pages.kaatru_weather.tps_visualization import tps_section
from pages.kaatru_weather.temp_sen55_visualization import temp_sen55_section
from pages.kaatru_weather.relative_humidity_sen55_visualization import relative_humidity_sen55_section
from pages.kaatru_weather.sunlight_sensors_visualization import sunlight_sensors_section


def kaatru_weather_dashboard():
    """
    Display weather dashboard for Kaatru data

    Returns:
    None: Displays the weather dashboard in Streamlit
    """
    st.title("Weather Dashboard Kaatru Data")

    # Overview
    st.write("## Kaatru Weather Data")

    artefact_data_stats = get_artefact_data_stats(3)
    
    if not artefact_data_stats.empty and not pd.isna(artefact_data_stats['min_ts'].iloc[0]):
        st.write(
            f"Data Available From {artefact_data_stats['min_ts'].iloc[0].date()} to {artefact_data_stats['max_ts'].iloc[0].strftime('%Y-%m-%d %H:%M:%S')} for {int(artefact_data_stats['num_days'].iloc[0])} days"
        )
    else:
        st.write("No data available in the database for Kaatru Weather.")
        return

    # Add tabs for different sections
    tabs = st.tabs(
        [
            "Temperature",
            "Relative Humidity",
            "Wind Speed",
            "Rain",
            "Particle Matter Mass",
            "Particle Matter Number",
            "TPS",
            "Temp sen55",
            "Relative Humidity sen55",
            "Sunlight Sensors",
        ]
    )

    # Temperature Section
    with tabs[0]:
        temperature_section()

    # Relative Humidity Section
    with tabs[1]:
        relative_humidity_section()

    # Wind Speed Section
    with tabs[2]:
        wind_speed_section()

    # Rain Section
    with tabs[3]:
        rain_section()

    # Particle Matter Mass Section
    with tabs[4]:
        pm_section()

    # Particle Matter Number Section
    with tabs[5]:
        npm_number_section()

    # TPS Section
    with tabs[6]:
        tps_section()

    # Temp sen55 Section
    with tabs[7]:
        temp_sen55_section()

    # Relative Humidity sen55 Section
    with tabs[8]:
        relative_humidity_sen55_section()

    # Sunlight Sensors Section
    with tabs[9]:
        sunlight_sensors_section()
