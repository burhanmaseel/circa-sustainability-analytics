import streamlit as st
import pandas as pd
from utils.grid_metrics import (
    calculate_total_import_export_grid,
    calculate_import_export_stats,
    calculate_total_import_export_efficiency
)
from utils.data_reader import get_artefact_attributes_data
from utils.streamlit_visualization import create_interactive_chart

def grid_impex_section():
    st.write("### Grid Import/Export")

    artefact_type_attributes = ('studer_grid_imp_exp_l1', 'studer_grid_imp_exp_l2', 'studer_grid_imp_exp_l3')
    results = get_artefact_attributes_data(artefact_type_attributes)

    with st.expander("View Data Sample"):
        st.write(results.head(100))

    # Total Import/Export
    total_export, exp_l1, exp_l2, exp_l3 = calculate_total_import_export_grid(results)
    st.write(f"**Total Solar Export to Grid:** {total_export:.2f} (Units)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Export L1", f"{exp_l1:.2f}")
    col2.metric("Export L2", f"{exp_l2:.2f}")
    col3.metric("Export L3", f"{exp_l3:.2f}")
    
    # Efficiency
    export_inst, import_inst, eff = calculate_total_import_export_efficiency(results)
    st.write(f"**Import/Export Efficiency (Export %):** {eff*100:.2f}%")
    st.write(f"Export Instances: {export_inst}, Import Instances: {import_inst}")

    # Stats
    st.write("### Import/Export Statistics")
    stats = calculate_import_export_stats(results)
    st.dataframe(stats, hide_index=True)

    # Chart
    st.write("### Grid Import/Export Over Time")
    chart_data = results.copy()
    chart_data['ts'] = pd.to_datetime(chart_data['ts'])
    chart_data['numeric_value'] = pd.to_numeric(chart_data['numeric_value'], errors='coerce')
    
    pivot_chart_data = chart_data.pivot(index='ts', columns='attribute_name', values='numeric_value')
    
    create_interactive_chart(
        pivot_chart_data,
        "Grid Import (Positive) / Export (Negative)"
    )