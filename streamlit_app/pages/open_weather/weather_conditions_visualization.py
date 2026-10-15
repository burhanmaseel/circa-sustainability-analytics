import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from utils.weather_data import get_weather_summary, handle_missing_data
from utils.data_reader import get_artefact_attributes_data

def weather_conditions_section():
    """
    Display weather conditions section in the weather dashboard
    """
    st.write("### Weather Conditions Analysis")
    
    artefact_type_attributes = ('weather_main', 'weather_description', 'weather_id', 'humidity', 'pressure', 'wind_speed', 'wind_degree')
    results = get_artefact_attributes_data(artefact_type_attributes)

    if results.empty:
        st.write("No data available in DB for Weather Conditions.")
        return

    # Pivot data
    chart_data = results.copy()
    chart_data['ts'] = pd.to_datetime(chart_data['ts'])
    
    # Merge numeric and text values
    if 'text_value' in chart_data.columns:
        chart_data['value_to_use'] = chart_data['numeric_value'].fillna(chart_data['text_value'])
    else:
        chart_data['value_to_use'] = chart_data['numeric_value']
        
    weather_data = chart_data.pivot(index='ts', columns='attribute_name', values='value_to_use')
    
    # Rename columns to match existing logic
    rename_map = {
        'wind_degree': 'wind_deg'
    }
    weather_data = weather_data.rename(columns=rename_map)
    weather_data.index.name = 'dt'

    
    # Handle missing data
    for col in ['weather_main', 'weather_description', 'weather_id']:
        if col in weather_data.columns:
            weather_data = handle_missing_data(weather_data, col)
    
    # Weather conditions summary
    st.write("#### Weather Conditions Summary")
    if 'weather_main' in weather_data.columns:
        weather_summary = get_weather_summary(weather_data, 'weather_main')
        
        # Display as table
        summary_df = pd.DataFrame(weather_summary).reset_index()
        summary_df.columns = ['Weather Condition', 'Count']
        summary_df['Percentage'] = (summary_df['Count'] / summary_df['Count'].sum() * 100).round(2)
        st.write(summary_df)
        
        # Display as pie chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(summary_df['Count'], labels=summary_df['Weather Condition'], 
               autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title("Distribution of Weather Conditions")
        st.pyplot(fig)
    else:
        st.write("No weather condition data available.")
    
    # Weather conditions over time
    st.write("#### Weather Conditions Over Time")
    if 'weather_main' in weather_data.columns:
        # Create a pivot table for weather conditions over time
        # Resample to daily frequency to avoid overcrowding
        daily_weather = weather_data.reset_index()
        daily_weather['date'] = daily_weather['dt'].dt.date
        daily_counts = daily_weather.groupby(['date', 'weather_main']).size().unstack(fill_value=0)
        
        # Plot stacked bar chart for weather conditions over time
        if not daily_counts.empty:
            fig, ax = plt.subplots(figsize=(14, 7))
            daily_counts.plot(kind='bar', stacked=True, ax=ax, colormap='viridis')
            ax.set_title("Daily Weather Conditions")
            ax.set_xlabel("Date")
            ax.set_ylabel("Count")
            ax.legend(title="Weather Condition")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.write("Insufficient data for daily weather conditions chart.")
    else:
        st.write("No weather condition data available for time series analysis.")
    
    # Weather descriptions
    st.write("#### Detailed Weather Descriptions")
    if 'weather_description' in weather_data.columns:
        # Get unique descriptions and their counts
        desc_counts = weather_data['weather_description'].value_counts()
        desc_df = pd.DataFrame(desc_counts).reset_index()
        desc_df.columns = ['Description', 'Count']
        desc_df['Percentage'] = (desc_df['Count'] / desc_df['Count'].sum() * 100).round(2)
        
        # Display top 10 descriptions
        st.write("Top 10 Weather Descriptions:")
        st.write(desc_df.head(10))
    else:
        st.write("No detailed weather description data available.")
    
    # Weather IDs analysis
    st.write("#### Weather ID Analysis")
    if 'weather_id' in weather_data.columns:
        # Group weather IDs by their first digit (weather category)
        weather_data['weather_category'] = weather_data['weather_id'].astype(str).str[0]
        category_map = {
            '2': 'Thunderstorm',
            '3': 'Drizzle',
            '5': 'Rain',
            '6': 'Snow',
            '7': 'Atmosphere',
            '8': 'Clear/Clouds',
            '9': 'Extreme'
        }
        weather_data['weather_category_name'] = weather_data['weather_category'].map(category_map).fillna('Other')
        
        # Count by category
        category_counts = weather_data['weather_category_name'].value_counts()
        cat_df = pd.DataFrame(category_counts).reset_index()
        cat_df.columns = ['Category', 'Count']
        cat_df['Percentage'] = (cat_df['Count'] / cat_df['Count'].sum() * 100).round(2)
        
        # Display as table
        st.write("Weather Categories:")
        st.write(cat_df)
        
        # Display as bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(cat_df['Category'], cat_df['Count'], color='purple', alpha=0.7)
        ax.set_title("Weather Categories")
        ax.set_xlabel("Category")
        ax.set_ylabel("Count")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.write("No weather ID data available.")
