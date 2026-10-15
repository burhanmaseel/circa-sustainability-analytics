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
from pages.open_weather.temperature_visualization import temperature_section
from pages.open_weather.visibility_visualization import visibility_section
from pages.open_weather.dew_point_visualization import dew_point_section
from pages.open_weather.weather_conditions_visualization import weather_conditions_section
from pages.open_weather.clouds_visualization import clouds_section


def weather_dashboard_open_weather():
    """
    Display weather dashboard for Open Weather data

    Returns:
    None: Displays the weather dashboard in Streamlit
    """
    st.title("Weather Dashboard - Open Weather")

    # Overview
    st.write("## Open Weather Data")

    artefact_data_stats = get_artefact_data_stats(4)
    
    if not artefact_data_stats.empty and not pd.isna(artefact_data_stats['min_ts'].iloc[0]):
        st.write(
            f"Data Available From {artefact_data_stats['min_ts'].iloc[0].date()} to {artefact_data_stats['max_ts'].iloc[0].strftime('%Y-%m-%d %H:%M:%S')} for {int(artefact_data_stats['num_days'].iloc[0])} days"
        )
    else:
        st.write("No data available in the database for Open Weather.")
        return

    # Add tabs for different sections
    tabs = st.tabs(
        ["Temperature", "Visibility", "Dew Point", "Weather Conditions", "Clouds"]
    )

    # Temperature Section
    with tabs[0]:
        temperature_section()

    # Visibility Section
    with tabs[1]:
        visibility_section()

    # Dew Point Section
    with tabs[2]:
        dew_point_section()

    # Weather Conditions Section
    with tabs[3]:
        weather_conditions_section()

    # Clouds Section
    with tabs[4]:
        clouds_section()
