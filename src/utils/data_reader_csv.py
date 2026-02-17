'''
This module is used to read data from direct CSV files.
LEGACY CODE - DO NOT USE - USE data_reader.py INSTEAD
'''

import pandas as pd
import glob
import csv
import os
from sqlalchemy import text
from dotenv import load_dotenv


from config.studer_constants import studer_names, required_studer_columns
from config.openweather_weather_constants import required_weather_columns
from config.kaatru_weather_constants import required_kaatru_weather_columns

def read_studer_data_directory(directory, return_raw_data=False, set_index=True):
    all_files = glob.glob(os.path.join(directory, "*.csv"), recursive=True) + glob.glob(
        os.path.join(directory, "*.CSV"), recursive=True
    )
    li = []
    for filename in all_files:
        df = pd.read_csv(
            filename,
            skiprows=3,
            index_col=False,
            header=None,
            on_bad_lines="skip",
            encoding="utf-8",
            quoting=csv.QUOTE_NONE,
        )

        if df.columns.__len__() == 77:
            print(filename)
            print(df.columns.__len__())
            df_updated = df.drop(columns=df.columns[-2:], axis=1)
            data = df_updated.iloc[:1440, :]
            li.append(data)

    studer_raw_data = pd.concat(li, axis=0, ignore_index=True)
    studer_raw_data.columns = studer_names

    if not return_raw_data:
        studer_raw_data = studer_raw_data[required_studer_columns]

    if set_index:
        studer_raw_data["Timestamp"] = pd.to_datetime(
            studer_raw_data["Timestamp"], format="%d.%m.%Y %H:%M", dayfirst=True, errors='coerce'
        )
        studer_raw_data.set_index("Timestamp", inplace=True)
        studer_raw_data.sort_index(inplace=True)

    return studer_raw_data



def read_enphase_panel_data_file(file_directory, file_name, set_index=True):
    file_path = os.path.join(file_directory, file_name)
    data = pd.read_csv(
        file_path, index_col=False, header=0, on_bad_lines="skip", encoding="utf-8"
    )

    if set_index:
        data["Date"] = pd.to_datetime(
            data[["Year", "Month", "Day"]].astype(str).agg("-".join, axis=1),
            dayfirst=True,
        )
        data.drop(["Year", "Month", "Day"], axis=1, inplace=True)
        data.set_index("Date", inplace=True)
        data.sort_index(inplace=True)

    # Ensure the index is timezone-naive for better compatibility
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    return data


def read_enphase_15min_data_file(file_directory, file_name, set_index=True, format="%d/%m/%Y %H:%M"):
    """Read 15-minute Enphase energy data file"""
    file_path = os.path.join(file_directory, file_name)
    data = pd.read_csv(
        file_path, index_col=False, header=0, on_bad_lines="skip", encoding="utf-8"
    )

    if set_index:
        data["Date"] = pd.to_datetime(data["Date/Time"], format=format)
        data.drop("Date/Time", axis=1, inplace=True)
        data.set_index("Date", inplace=True)
        data.sort_index(inplace=True)

    # Ensure the index is timezone-naive for better compatibility
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    return data


def read_solar_data_file(file_name):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    file_name = os.path.join(project_root, "data", "sample", "solar", file_name)

    data = pd.read_csv(
        file_name,
        index_col=False,
        header=0,
        on_bad_lines="skip",
        encoding="utf-8",
        sep=";",
    )
    return data


def read_open_weather_data_file(file_directory, file_name, set_index=True, filter_columns=True):
    file_path = os.path.join(file_directory, file_name)

    data = pd.read_csv(
        file_path, index_col=False, header=0, on_bad_lines="skip", encoding="utf-8"
    )

    if filter_columns:
        data = data[required_weather_columns]

    if set_index:
        data["dt"] = pd.to_datetime(data["dt"], unit="s", errors="coerce")
        data.set_index("dt", inplace=True)
        data.sort_index(inplace=True)

    return data


def read_raw_weather_kaatru_data_file(file_name):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    file_name = os.path.join(
        project_root, "data", "sample", "weather", "kaatru", file_name
    )

    data = pd.read_csv(
        file_name,
        index_col=False,
        header=0,
        on_bad_lines="skip",
        encoding="utf-8",
        low_memory=False,
    )
    data["srvtime"] = pd.to_datetime(data["srvtime"], unit="ms", errors="coerce")
    data.set_index("srvtime", inplace=True)
    data.sort_index(inplace=True)

    return data


def read_filtered_weather_kaatru_data_file(file_name):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    file_name = os.path.join(
        project_root, "data", "sample", "weather", "kaatru", file_name
    )

    data = pd.read_csv(
        file_name,
        index_col=False,
        header=0,
        on_bad_lines="skip",
        encoding="utf-8",
        low_memory=False,
    )
    data["srvtime"] = pd.to_datetime(data["srvtime"], unit="ms", errors="coerce")
    data = data[required_kaatru_weather_columns]
    data.set_index("srvtime", inplace=True)
    data.sort_index(inplace=True)

    return data


def read_weather_kaatru_data_directory(directory):
    all_files = glob.glob(os.path.join(directory, "*.csv"), recursive=True) + glob.glob(
        os.path.join(directory, "*.CSV"), recursive=True
    )
    all_files = list(set(all_files))
    li = []
    for filename in all_files:
        df = pd.read_csv(
            filename,
            index_col=False,
            header=0,
            on_bad_lines="skip",
            encoding="utf-8",
            low_memory=False,
        )
        li.append(df)

    weather_data = pd.concat(li, axis=0, ignore_index=True)

    weather_data["datetime"] = pd.to_datetime(
        weather_data["srvtime"], unit="ms", errors="coerce"
    )
    weather_data.set_index("datetime", inplace=True)
    weather_data.sort_index(inplace=True)

    return weather_data

