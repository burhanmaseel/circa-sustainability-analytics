import streamlit as st
import plotly.graph_objects as go

def create_metric_section(title, value, data_df, chart_columns=None, y_min=None, y_max=None):
    st.write(f"### {title}")
    st.write(value)

    if chart_columns is None:
        chart_columns = list(data_df.columns)
        chart_columns.remove('Timestamp')

    # Create container for parameter selection
    select_container = st.container()
    plot_container = st.empty()

    with select_container:
        selected_param = st.selectbox(f"Select parameter for {title}", chart_columns)

    # Create the chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data_df['Timestamp'],
        y=data_df[selected_param],
        name=selected_param,
        mode='lines'
    ))

    fig.update_layout(
        title=f'{selected_param} Over Time',
        yaxis_title=selected_param,
        xaxis_title='Timestamp',
        width=900,
        height=570
    )

    if y_min is not None and y_max is not None:
        fig.update_yaxes(range=[y_min, y_max])

    st.write(fig)
    st.write(data_df)

def create_interactive_chart(df, title, y_col=None, y_min=None, y_max=None):
    """Create an interactive Plotly chart with parameter selection."""
    # Create containers
    select_container = st.container()
    
    # Get available parameters
    param_lst = list(df.columns)
    
    # Parameter selection
    with select_container:
        selected_param = y_col if y_col else st.selectbox(f"Select parameter for {title}", param_lst)

    # Create chart
    fig = go.Figure()
    
    # Main data trace
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[selected_param],
        name=selected_param,
        mode='lines',
        line=dict(width=1.5, color='#0073e6'),
        hovertemplate='%{y:.2f}<br>%{x}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title={
            'text': f'{selected_param} Over Time',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title=selected_param,
        xaxis_title='Timestamp',
        hovermode="x unified",
        template="plotly_white",
        height=600,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Add range slider
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=12, label="12h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    # Set Y-axis range and add reference lines if provided
    if y_min is not None and y_max is not None:
        fig.update_yaxes(range=[y_min - 5, y_max + 5]) # Add a little buffer
        
        # Add limit lines
        fig.add_hline(y=y_min, line_dash="dash", line_color="red", annotation_text=f"Min ({y_min})", annotation_position="bottom right")
        fig.add_hline(y=y_max, line_dash="dash", line_color="red", annotation_text=f"Max ({y_max})", annotation_position="top right")

    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander(f"View {title} Data"):
        st.dataframe(df, use_container_width=True)