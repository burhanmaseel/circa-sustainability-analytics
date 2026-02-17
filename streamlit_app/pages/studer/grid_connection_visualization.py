import streamlit as st
import pandas as pd
from utils.grid_metrics import (
    calculate_total_grid_disconnected_instances, 
    calculate_total_grid_disconnected_days
)
from utils.data_reader import get_artefact_attributes_data
from utils.streamlit_visualization import create_interactive_chart

def grid_connection_section():
    st.write("### Grid Connection Section")

    artefact_type_attributes = ('grid_status_l1', 'grid_status_l2', 'grid_status_l3')
    results = get_artefact_attributes_data(artefact_type_attributes)

    # Sample Data
    with st.expander("View Data Sample"):
        st.write(results.head(100))

    # Disconnected Instances
    st.write("### Total Grid Disconnected Instances")
    st.write('Instances are calculated based on each data row i.e. per minute data')
    grid_disconnected_instances = calculate_total_grid_disconnected_instances(results)
    st.dataframe(grid_disconnected_instances, hide_index=True)

    # Disconnected Days
    st.write("### Total Grid Disconnected Days")
    st.write('Days are calculated based on each data row i.e. per minute data')
    total_grid_disconnected_days = calculate_total_grid_disconnected_days(results)
    st.dataframe(total_grid_disconnected_days, hide_index=True)

    # Grid Status Chart
    st.write("### Grid Status Chart")
    
    # Process data for chart
    chart_data = results.copy()
    chart_data['ts'] = pd.to_datetime(chart_data['ts'])
    chart_data['numeric_value'] = pd.to_numeric(chart_data['numeric_value'], errors='coerce')
    
    # Pivot for visualization: Index=ts, Columns=attribute_name, Values=numeric_value
    pivot_chart_data = chart_data.pivot(index='ts', columns='attribute_name', values='numeric_value')
    
    create_interactive_chart(
        pivot_chart_data,
        "Grid Status (1=Connected, 0=Disconnected)",
        y_min=-0.1,
        y_max=1.1
    )