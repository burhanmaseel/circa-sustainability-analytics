import pandas as pd
import glob
import csv
import os
from datetime import timedelta
from sqlalchemy import text
from dotenv import load_dotenv

from db.connection import get_connection, get_sqlalchemy_engine

### DB Queries Starting Here ###

def get_artefact_types():
    engine = get_sqlalchemy_engine()

    query = """
        SELECT * FROM public.artefacttype
        ORDER BY id ASC
    """
    df = pd.read_sql(query, engine)

    return df


def get_artefact_type_attributes(artefact_type):
    engine = get_sqlalchemy_engine()

    query = """
        SELECT id, attribute_name FROM public.artefacttypeattribute
        WHERE artefact_type_id = %s
        ORDER BY id ASC
    """
    df = pd.read_sql(query, engine, params = (artefact_type,))

    return df


def get_artefact_attributes_data(artefacts_type_attributes, filters_dict = None):
    '''
    This function gets the values for all the type attributes passed to it
    e.g. ('grid_input_voltage_l1', 'grid_input_voltage_l2', 'grid_input_voltage_l3')

    :param artefacts_type_attributes: Type attributes
    :param filters_dict: Filters
    '''
    engine = get_sqlalchemy_engine()

    query_base = """
        SELECT
            ali.ts, ali.date, ali.hour, ali.minute, ali.second,
            ata.id, ata.attribute_name, alav.numeric_value, alav.text_value
        FROM public.artefactlogattributevalue alav
        INNER JOIN artefactloginstance ali
            ON alav.artefact_log_instance_id = ali.id
        INNER JOIN artefacttypeattribute ata
            ON ata.id = alav.artefact_type_attribute_id
        WHERE attribute_name IN :attr_names
    """

    params = {"attr_names": tuple(artefacts_type_attributes)}

    # 2. Dynamically append filters
    if filters_dict:
        for column, value in filters_dict.items():
            # Append "AND column = :column" to the query
            query_base += f" AND {column} = :{column}"
            params[column] = value

    query_base += "ORDER BY ata.id, ali.ts ASC"

    df = pd.read_sql(text(query_base), engine, params=params)

    return df
    

def get_all_artefact_types_data(artefact_type, filters=''):
    '''
    This function gets the values for all the type attributes for the given artefact type id
    e.g. values:
        # STUDER = 1
        # ENPHASE = 2
        # WEATHER STATION = 3
        # WEATHER REPORT = 4

    :param artefacts_type_attributes: Type attributes
    :param filters_dict: Filters
    '''
    engine = get_sqlalchemy_engine()

    query = """
        SELECT
            ali.ts, ali.date, ali.hour, ali.minute, ali.second,
            ata.id, ata.attribute_name, alav.numeric_value, alav.text_value
        FROM public.artefactlogattributevalue alav
        INNER JOIN artefactloginstance ali
            ON alav.artefact_log_instance_id = ali.id
        INNER JOIN (
            SELECT id, attribute_name
            FROM artefacttypeattribute
            WHERE artefact_type_id = %s
        ) ata
            ON ata.id = alav.artefact_type_attribute_id
        ORDER BY ata.id, ali.ts ASC
    """
    df = pd.read_sql(query, engine, params=(artefact_type,))

    return df


def get_artefact_data_stats(artefact_type):
    engine = get_sqlalchemy_engine()

    query = """
        SELECT
            COUNT(DISTINCT(date)) as num_days, min(ts) as min_ts, max(ts) as max_ts
        FROM public.artefactloginstance
        WHERE artefact_id IN (
            SELECT id FROM public.artefact
            WHERE artefact_type_id = %s
        )
    """
    df = pd.read_sql(query, engine, params=(artefact_type,))

    return df

def get_open_weather_temperature_data():
    engine = get_sqlalchemy_engine()
    query = """
        SELECT date_time as ts, temperature as temp, feels_like_temperature as feels_like, 
               temperature_min as temp_min, temperature_max as temp_max 
        FROM public.open_weather 
        ORDER BY date_time ASC
    """
    df = pd.read_sql(query, engine)
    return df


def get_enphase_15min_data(start_date=None, end_date=None):
    """
    Fetch 15-minute interval Enphase energy data from the v_enphase view.

    Returns a DataFrame indexed by timestamp with columns:
        energy_produced, energy_consumed, grid_exported, grid_imported

    :param start_date: Optional start date filter (date or str)
    :param end_date:   Optional end date filter (date or str, inclusive)
    """
    engine = get_sqlalchemy_engine()

    params = {}
    date_filter = ""

    # Compute the exclusive upper bound in Python so psycopg2 only passes
    # plain date strings — avoids the INTERVAL type-parsing error.
    if start_date is not None and end_date is not None:
        end_exclusive = pd.Timestamp(end_date) + timedelta(days=1)
        date_filter = "WHERE date >= %(start_date)s AND date < %(end_date_excl)s"
        params["start_date"] = str(start_date)
        params["end_date_excl"] = end_exclusive.strftime("%Y-%m-%d")
    elif start_date is not None:
        date_filter = "WHERE date >= %(start_date)s"
        params["start_date"] = str(start_date)
    elif end_date is not None:
        end_exclusive = pd.Timestamp(end_date) + timedelta(days=1)
        date_filter = "WHERE date < %(end_date_excl)s"
        params["end_date_excl"] = end_exclusive.strftime("%Y-%m-%d")

    query = f"""
        SELECT
            date,
            energy_produced,
            energy_consumed,
            grid_exported,
            grid_imported
        FROM public.v_enphase
        {date_filter}
        ORDER BY date ASC
    """

    df = pd.read_sql(query, engine, params=params if params else None)

    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)

    # Ensure numeric types
    for col in ["energy_produced", "energy_consumed", "grid_exported", "grid_imported"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


def get_enphase_date_range():
    """
    Return the (min_date, max_date) of all Enphase records in the database.
    Uses the v_enphase view (artefact_id = 2).
    Returns a tuple of (datetime.date, datetime.date) or (None, None) if no data.
    """
    engine = get_sqlalchemy_engine()
    query = """
        SELECT MIN(date)::date AS min_date, MAX(date)::date AS max_date
        FROM public.v_enphase
    """
    df = pd.read_sql(query, engine)
    if df.empty or df["min_date"].iloc[0] is None:
        return None, None
    return df["min_date"].iloc[0], df["max_date"].iloc[0]


