import streamlit as st
import pandas as pd
from utils.data_reader import get_artefact_attributes_data

def rain_section():
    """
    Display Rain section.
    """
    st.subheader("Rain")
    
    artefact_type_attributes = ('value.rain',)
    results = get_artefact_attributes_data(artefact_type_attributes)

    if results.empty:
        st.write("No data available in DB for Rain.")
        return

    # Pivot data
    chart_data = results.copy()
    chart_data['ts'] = pd.to_datetime(chart_data['ts'])
    chart_data['numeric_value'] = pd.to_numeric(chart_data['numeric_value'], errors='coerce')
    data = chart_data.pivot(index='ts', columns='attribute_name', values='numeric_value')
    
    st.write("Rain data visualization goes here.")
    with st.expander("View Data Sample"):
        st.dataframe(data.head(100))
