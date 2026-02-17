import streamlit as st
import pandas as pd
from utils.streamlit_visualization import create_interactive_chart
from utils.grid_metrics import calculate_total_load_shedding_instances, calculate_total_load_shedding_days, calculate_long_duration_voltage_variation
from utils.data_reader import get_artefact_attributes_data

def voltage_section():
    st.write("### Voltage Section")

    artefact_type_attributes = ('grid_input_voltage_l1', 'grid_input_voltage_l2', 'grid_input_voltage_l3')
    results = get_artefact_attributes_data(artefact_type_attributes)

    # Sample Data
    with st.expander("View Data Sample"):
        st.write(results.head(100))

    # Total Load Shedding Instances
    st.write("### Total Load Shedding Instances")
    st.write('Instances are calculated based on each data row i.e. per minute data')
    load_shedding_instances = calculate_total_load_shedding_instances(results)
    st.dataframe(load_shedding_instances, hide_index=True)

    # Total Load Shedding Days
    st.write("### Total Load Shedding Days")
    st.write('Days are calculated based on each data row i.e. per minute data')
    total_load_shedding_days = calculate_total_load_shedding_days(results)
    st.dataframe(total_load_shedding_days, hide_index=True)

    # Voltage Variation Section
    voltage_variation_instances = calculate_long_duration_voltage_variation(results)
    st.write("### Voltage Variation Instances")
    st.write('Instances are calculated based on each 10 minute interval')
    st.dataframe(voltage_variation_instances, hide_index=True)

    # Load Shedding Section
    st.write("### Load Shedding Chart")
    
    # Process data for chart
    chart_data = results.copy()
    chart_data['ts'] = pd.to_datetime(chart_data['ts'])
    chart_data['numeric_value'] = pd.to_numeric(chart_data['numeric_value'], errors='coerce')
    
    # Pivot for visualization: Index=ts, Columns=attribute_name, Values=numeric_value
    pivot_chart_data = chart_data.pivot(index='ts', columns='attribute_name', values='numeric_value')
    
    create_interactive_chart(
        pivot_chart_data,
        "Load Shedding",
        y_min=190,
        y_max=260
    )