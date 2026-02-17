import streamlit as st
import pandas as pd
from utils.grid_metrics import (
    calculate_total_wrong_frequency_instances, 
    calculate_total_wrong_frequency_days, 
    calculate_frequency_stats,
    calculate_long_duration_frequency_variation
)
from utils.streamlit_visualization import create_interactive_chart
from utils.data_reader import get_artefact_attributes_data

def frequency_section():
    st.write("### Frequency Section")
    
    artefact_type_attributes = ('grid_input_frequency_l1', 'grid_input_frequency_l2', 'grid_input_frequency_l3')
    results = get_artefact_attributes_data(artefact_type_attributes)

    # Sample Data
    with st.expander("View Data Sample"):
        st.write(results.head(100))

    # Wrong Frequency Instances
    st.write("### Total Wrong Frequency Instances")
    st.write('Instances are calculated based on each data row i.e. per minute data')
    wrong_freq_instances = calculate_total_wrong_frequency_instances(results)
    st.dataframe(wrong_freq_instances, hide_index=True)

    # Wrong Frequency Days
    st.write("### Total Wrong Frequency Days")
    st.write('Days are calculated based on each data row i.e. per minute data')
    total_wrong_frequency_days = calculate_total_wrong_frequency_days(results)
    st.dataframe(total_wrong_frequency_days, hide_index=True)

    # Power Frequency Variation Section
    st.write("### Power Frequency Variation Instances")
    st.write('Instances are calculated based on each 10 minute interval')
    freq_variation_instances = calculate_long_duration_frequency_variation(results)
    st.dataframe(freq_variation_instances, hide_index=True)

    # Frequency Stats
    st.write("### Frequency Stats")
    frequency_stats = calculate_frequency_stats(results)
    st.dataframe(frequency_stats, hide_index=True)

    # Frequency Chart
    st.write("### Frequency Chart")
    
    # Process data for chart
    chart_data = results.copy()
    chart_data['ts'] = pd.to_datetime(chart_data['ts'])
    chart_data['numeric_value'] = pd.to_numeric(chart_data['numeric_value'], errors='coerce')
    
    # Pivot for visualization: Index=ts, Columns=attribute_name, Values=numeric_value
    pivot_chart_data = chart_data.pivot(index='ts', columns='attribute_name', values='numeric_value')
    
    create_interactive_chart(
        pivot_chart_data,
        "Grid Input Frequencies",
        y_min=48, 
        y_max=52
    )