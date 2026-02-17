import pandas as pd


def calculate_total_load_shedding_instances(df):
    result = (
        df[df['numeric_value'] < 190]
        .groupby('attribute_name')['numeric_value']
        .count()
        .reset_index()
    )

    result.columns = ['Phase', 'Load Shedding Instance Count']
    result['Phase'] = result['Phase'].str.replace('grid_input_voltage_l', 'Phase ')

    return result

def calculate_total_load_shedding_days(df):
    """
    Calculates the number of days with load shedding events for each phase.

    Args:
        df (pd.DataFrame): A DataFrame containing grid metrics data with 'date', 
                           'attribute_name', and 'numeric_value' columns.

    Returns:
        pd.DataFrame: A DataFrame summarizing load shedding statistics per phase, 
                      including total days, load shedding days, non-load shedding days, 
                      and grid efficiency.
    """
    df = df.set_index('date')
    total_days = len(df.groupby(df.index))
    
    if total_days == 0:
        return pd.DataFrame(columns=['Phase', 'Load Shedding Days', 'Non-Load Shedding Days', 'Grid Efficiency'])

    # Filter for load shedding check (< 190V) and calculate unique days per phase
    result = (
        df[df['numeric_value'] < 190]
        .groupby('attribute_name')
        .apply(lambda x: len(x.index.unique()), include_groups=False)
        .reset_index()
    )
    
    result.columns = ['Phase', 'Load Shedding Days']
    result['Phase'] = result['Phase'].str.replace('grid_input_voltage_l', 'Phase ')
    result['Non-Load Shedding Days'] = total_days - result['Load Shedding Days']
    result['Total Days'] = total_days
    result['Downtime Percentage'] = ((result['Load Shedding Days'] / total_days) * 100).round(2)
    
    return result

def calculate_long_duration_voltage_variation(df):
    """
    Calculates the number of 10-minute intervals where the average voltage 
    is outside the acceptable range (190V - 260V) for each phase.
    """
    df = df.copy()
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    df = df.set_index('date').sort_index()

    def count_violations(group):
        # Resample to 10 minutes and calculate mean
        # Fill missing values to ensure continuous timeline or handle periods with no data
        # For this metric, we skip intervals with no data, so strictly resampling is enough
        means = group.resample('10min').mean()
        return ((means <= 190) | (means >= 260)).sum()

    result = (
        df.groupby('attribute_name')['numeric_value']
        .apply(count_violations)
        .reset_index()
    )

    result.columns = ['Phase', 'Long Duration Voltage Variation Instances']
    result['Phase'] = result['Phase'].str.replace('grid_input_voltage_l', 'Phase ')

    return result


def calculate_total_wrong_frequency_instances(df):
    """
    Calculates the number of instances where frequency is outside 49-51 Hz for each phase.
    """
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    result = (
        df[(df['numeric_value'] < 49) | (df['numeric_value'] > 51)]
        .groupby('attribute_name')['numeric_value']
        .count()
        .reset_index()
    )

    result.columns = ['Phase', 'Wrong Frequency Instances']
    result['Phase'] = result['Phase'].str.replace('grid_input_frequency_l', 'Phase ')

    return result

def calculate_total_wrong_frequency_days(df):
    """
    Calculates the number of days with wrong frequency events for each phase.
    """
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
        
    df = df.set_index('date')
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    total_days = len(df.groupby(df.index))
    
    if total_days == 0:
        return pd.DataFrame(columns=['Phase', 'Wrong Frequency Days', 'Normal Frequency Days', 'Frequency Efficiency'])

    # Filter for wrong frequency check (< 49Hz or > 51Hz)
    result = (
        df[(df['numeric_value'] < 49) | (df['numeric_value'] > 51)]
        .groupby('attribute_name')
        .apply(lambda x: len(x.index.unique()), include_groups=False)
        .reset_index()
    )
    
    result.columns = ['Phase', 'Wrong Frequency Days']
    result['Phase'] = result['Phase'].str.replace('grid_input_frequency_l', 'Phase ')
    result['Total Days'] = total_days
    result['Normal Frequency Days'] = total_days - result['Wrong Frequency Days']
    result['Frequency Stability %'] = ((result['Normal Frequency Days'] / total_days) * 100).round(2)
    
    return result

def calculate_frequency_stats(df):
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    stats = df.groupby('attribute_name')['numeric_value'].agg(['min', 'max', 'mean', 'std', 'count']).reset_index()
    stats.columns = ['Phase', 'Min', 'Max', 'Average', 'Standard Deviation', 'Total Instances']
    stats['Phase'] = stats['Phase'].str.replace('grid_input_frequency_l', 'Phase ')
    
    return stats

def calculate_long_duration_frequency_variation(df):
    """
    Calculates the number of 10-minute intervals where the average frequency
    is outside the acceptable range (49Hz - 51Hz) for each phase.
    """
    df = df.copy()
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    df = df.set_index('date').sort_index()

    def count_violations(group):
        # Resample to 10 minutes and calculate mean
        means = group.resample('10min').mean()
        return ((means <= 49) | (means >= 51)).sum()

    result = (
        df.groupby('attribute_name')['numeric_value']
        .apply(count_violations)
        .reset_index()
    )

    result.columns = ['Phase', 'Long Duration Frequency Variation Instances']
    result['Phase'] = result['Phase'].str.replace('grid_input_frequency_l', 'Phase ')

    return result

def calculate_total_grid_disconnected_instances(df):
    """
    Calculates the number of instances where grid status is disconnected (< 1) for each phase.
    """
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    result = (
        df[df['numeric_value'] < 1]
        .groupby('attribute_name')['numeric_value']
        .count()
        .reset_index()
    )

    result.columns = ['Phase', 'Grid Disconnected Instances']
    result['Phase'] = result['Phase'].str.replace('grid_status_l', 'Phase ')

    return result

def calculate_total_grid_disconnected_days(df):
    """
    Calculates the number of days with grid disconnection events for each phase.
    """
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
        
    df = df.set_index('date')
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    total_days = len(df.groupby(df.index))
    
    if total_days == 0:
        return pd.DataFrame(columns=['Phase', 'Disconnected Days', 'Connected Days', 'Grid Availability %'])

    # Filter for disconnection check (< 1)
    result = (
        df[df['numeric_value'] < 1]
        .groupby('attribute_name')
        .apply(lambda x: len(x.index.unique()), include_groups=False)
        .reset_index()
    )
    
    result.columns = ['Phase', 'Disconnected Days']
    result['Phase'] = result['Phase'].str.replace('grid_status_l', 'Phase ')
    result['Total Days'] = total_days
    result['Connected Days'] = total_days - result['Disconnected Days']
    result['Grid Availability %'] = ((result['Connected Days'] / total_days) * 100).round(2)
    
    return result

def calculate_average_battery_soc(df):
    """
    Calculates the average battery state of charge.
    """
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    return df['numeric_value'].mean()

def calculate_total_battery_drain_days(df):
    """
    Calculates the number of days where battery SOC drops below 10%.
    """
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
        
    df = df.set_index('date')
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    total_days = len(df.groupby(df.index))
    
    if total_days == 0:
        return 0, 0, 0

    # Filter for drain check (< 10%)
    drain_days_count = (
        df[df['numeric_value'] < 10]
        .index.nunique()
    )
    
    total_battery_charge_days = total_days - drain_days_count
    battery_support_efficiency = total_battery_charge_days / total_days if total_days > 0 else 0
    
    return drain_days_count, total_battery_charge_days, battery_support_efficiency

def calculate_battery_soc_stats(df):
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    stats = df['numeric_value'].agg(['min', 'max', 'mean', 'std', 'count']).to_frame().T
    stats.columns = ['Min', 'Max', 'Average', 'Standard Deviation', 'Total Instances']
    
    return stats

def calculate_total_import_export_grid(df):
    """
    Calculates total energy imported and exported. 
    Assumes negative numeric_value is export, positive is import.
    """
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    # Calculate sum per phase for export (negative values)
    export_df = df[df['numeric_value'] < 0]
    solar_export_per_phase = export_df.groupby('attribute_name')['numeric_value'].sum()
    
    solar_export_to_grid_l1 = solar_export_per_phase.get('studer_grid_imp_exp_l1', 0)
    solar_export_to_grid_l2 = solar_export_per_phase.get('studer_grid_imp_exp_l2', 0)
    solar_export_to_grid_l3 = solar_export_per_phase.get('studer_grid_imp_exp_l3', 0)
    
    total_solar_export_to_grid = solar_export_to_grid_l1 + solar_export_to_grid_l2 + solar_export_to_grid_l3
    
    return total_solar_export_to_grid, solar_export_to_grid_l1, solar_export_to_grid_l2, solar_export_to_grid_l3

def calculate_import_export_stats(df):
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    stats = df.groupby('attribute_name')['numeric_value'].agg(['min', 'max', 'mean', 'std', 'count']).reset_index()
    stats.columns = ['Phase', 'Min', 'Max', 'Average', 'Standard Deviation', 'Total Instances']
    stats['Phase'] = stats['Phase'].str.replace('studer_grid_imp_exp_l', 'Phase ')
    
    return stats

def calculate_total_import_export_efficiency(df):
    """
    Calculates the number of instances of import vs export.
    """
    df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
    
    total_export_instances = (df['numeric_value'] < 0).sum()
    total_import_instances = (df['numeric_value'] > 0).sum()
    total_instances = len(df)
    
    import_export_efficiency = total_export_instances / total_instances if total_instances > 0 else 0

    return total_export_instances, total_import_instances, import_export_efficiency
