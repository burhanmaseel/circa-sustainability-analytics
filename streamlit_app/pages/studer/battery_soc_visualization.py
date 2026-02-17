import streamlit as st
import pandas as pd
from utils.grid_metrics import (
    calculate_average_battery_soc,
    calculate_total_battery_drain_days,
    calculate_battery_soc_stats
)
from utils.data_reader import get_artefact_attributes_data
from utils.streamlit_visualization import create_interactive_chart

def battery_soc_section():
    st.write("### Battery State of Charge")

    artefact_type_attributes = ('battery_state_of_charge',)
    results = get_artefact_attributes_data(artefact_type_attributes)

    with st.expander("View Data Sample"):
        st.write(results.head(100))

    # Average SOC
    avg_soc = calculate_average_battery_soc(results)
    st.write(f"**Average Battery SOC:** {avg_soc:.2f}%")

    # Metrics
    total_drain_days, total_charge_days, efficiency = calculate_total_battery_drain_days(results)
    
    if total_drain_days == 0 and total_charge_days == 0:
         st.write("No data available for drain days calculation.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Drain Days (<10%)", total_drain_days)
        col2.metric("Charge Days", total_charge_days)
        col3.metric("Efficiency", f"{efficiency*100:.2f}%")

    # Stats
    st.write("### SOC Statistics")
    stats = calculate_battery_soc_stats(results)
    st.dataframe(stats, hide_index=True)

    # Chart
    st.write("### Battery SOC Over Time")
    chart_data = results.copy()
    chart_data['ts'] = pd.to_datetime(chart_data['ts'])
    chart_data['numeric_value'] = pd.to_numeric(chart_data['numeric_value'], errors='coerce')
    
    pivot_chart_data = chart_data.pivot(index='ts', columns='attribute_name', values='numeric_value')
    
    create_interactive_chart(
        pivot_chart_data,
        "Battery SOC",
        y_min=0,
        y_max=100
    )