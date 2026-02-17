import pandas as pd
import glob
import csv
import os
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
            ata.id, ata.attribute_name, alav.numeric_value
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
            ata.id, ata.attribute_name, alav.numeric_value
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
        WHERE artefact_id = %s
    """
    df = pd.read_sql(query, engine, params=(artefact_type,))

    return df

