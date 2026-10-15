import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Hide Streamlit's auto-generated multi-page navigation (sidebar buttons).
# We use a custom dropdown instead.
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

from pages.kaatru_weather_dashboard import kaatru_weather_dashboard
# from pages.solar_panel_dashboard import solar_panel_dashboard
from pages.grid_metrics_dashboard import grid_metric_dashboard
from pages.enphase_15min_dashboard import enphase_15min_dashboard
from pages.enphase_15min_simple_dashboard import enphase_15min_simple_dashboard
# from pages.compare_3data import comparison_tables
from pages.open_weather_dashboard import weather_dashboard_open_weather

def home():
    st.write("# Sustainability Analytics Dashboard")

    st.sidebar.success("Select a Dashboard above.")

    st.markdown(
        """
        Welcome to our comprehensive sustainability analytics platform! This application provides various dashboards 
        to analyze and visualize sustainability metrics:

        ### Solar Panel Dashboard
        - Monitor solar panel performance and efficiency
        - Track energy generation patterns
        - Analyze environmental impact metrics

        ### Enphase 15-Min Energy Dashboard
        - 15-minute interval energy analytics per panel
        - Energy production, consumption, and grid import/export
        - Advanced time series analysis and daily pattern insights
        - Energy balance and self-consumption analytics

        ### Enphase Simple Analytics
        - Enphase daily energy analytics - all panels combined
        - Energy production, consumption, and grid import/export

        ### Grid Metric Dashboard
        - View real-time grid performance statistics
        - Analyze power distribution patterns
        - Monitor grid stability metrics

        ### Weather Dashboard - Open Weather
        - View real-time weather conditions and metrics
        - Analyze temperature, visibility, and other weather parameters
        - Monitor weather patterns and trends

        ### Weather Dashboard - Kaatru
        - View real-time weather conditions and metrics
        - Analyze temperature, visibility, and other weather parameters
        - Monitor weather patterns and trends

        ### Comparison Tables
        - Compare performance across different time periods
        - Analyze trends and patterns
        - View detailed metric breakdowns

        Choose a dashboard from the sidebar to explore detailed analytics and insights.
        """
    )

# page_names_to_funcs = {
#     "Home": home,
#     # "Solar Panel Dashboard": solar_panel_dashboard,
#     # "Enphase - All Panels Combined": enphase_15min_simple_dashboard,
#     # "Enphase 15-Min Energy Dashboard": enphase_15min_dashboard,
#     "Grid Metric Dashboard": grid_metric_dashboard
#     # "Weather Dashboard - Open Weather": weather_dashboard_open_weather,
#     # "Weather Dashboard - Kaatru": weather_dashboard_kaatru,
#     # "Comparison Tables": comparison_tables
# }

page_names_to_funcs = {
    "Home": home,
    "Grid Metric Dashboard": grid_metric_dashboard,
    "Enphase 15-Min Analytics": enphase_15min_dashboard,
    "Enphase Simple Analytics": enphase_15min_simple_dashboard,
    "Kaatru Weather Dashboard": kaatru_weather_dashboard,
    "Open Weather Dashboard": weather_dashboard_open_weather
}

demo_name = st.sidebar.selectbox("Choose a Dashboard", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
