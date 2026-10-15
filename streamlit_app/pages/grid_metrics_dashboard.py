import streamlit as st
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'src'))

from utils.data_reader import get_artefact_data_stats

from pages.studer.voltage_visualization import voltage_section
from pages.studer.frequency_visualization import frequency_section
from pages.studer.grid_connection_visualization import grid_connection_section
from pages.studer.battery_soc_visualization import battery_soc_section
from pages.studer.grid_impex_visualization import grid_impex_section

def grid_metric_dashboard():
    st.title("Grid Metrics Dashboard!")

    # Overview
    st.write("## Studer Data")

    artefact_data_stats = get_artefact_data_stats(1)
    st.write(f"Data Available From {artefact_data_stats['min_ts'].iloc[0].date()} to {artefact_data_stats['max_ts'].iloc[0].strftime('%Y-%m-%d %H:%M:%S')} for {int(artefact_data_stats['num_days'].iloc[0])} days")

    # Add tabs for different sections
    tabs = st.tabs(["Voltage", "Frequency", "Grid Connection", "Battery State", "Grid Import/Export"])

    # Voltage Section
    with tabs[0]:
        voltage_section()

    # Frequency Section
    with tabs[1]:
        frequency_section()

    # Grid Connection Section
    with tabs[2]:
        grid_connection_section()

    # Battery State Section
    with tabs[3]:
        battery_soc_section()

    # Grid Import/Export Section
    with tabs[4]:
        grid_impex_section()
