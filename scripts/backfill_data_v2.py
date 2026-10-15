"""
V2 Data Ingestion Pipeline - Complete, production-ready implementation.
Reads CSV files for Studer, Enphase, Open Weather, and Kaatru and ingests
them into the PostgreSQL EAV schema (artefactloginstance + artefactlogattributevalue).

Run order:
    1. python scripts/setup_test_db.py      # create/reset circa_test
    2. python scripts/seed_metadata_v2.py   # seed kaatru attrs + panel metadata
    3. python scripts/backfill_data_v2.py   # ingest all CSVs

By default targets circa_test. Change get_engine() to target production.
"""

import sys
import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.append(os.path.abspath('src'))
import utils.data_reader_csv as data_reader

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Engine — change DB_NAME here to target production
# ---------------------------------------------------------------------------
def get_engine(db_name="circa_test"):
    return create_engine(
        f"postgresql+psycopg2://postgres:root@127.0.0.1:5432/{db_name}"
    )


# ---------------------------------------------------------------------------
# Core EAV ingestion helper
# ---------------------------------------------------------------------------
def ingest_to_eav(df: pd.DataFrame, engine, artefact_type_id: int,
                  artefact_id: int, ts_col: str, metrics_cols: list,
                  fill_nan: float = 0.0):
    """
    Ingest a wide DataFrame into the EAV tables:
        artefactloginstance  — one row per unique timestamp
        artefactlogattributevalue — one row per (timestamp x attribute)

    Args:
        df              : Wide source DataFrame (one column per metric).
        engine          : SQLAlchemy engine pointing at the target DB.
        artefact_type_id: FK into artefacttype.
        artefact_id     : FK into artefact (the physical device record).
        ts_col          : Column name in df that holds the timestamp.
        metrics_cols    : List of column names (already renamed to DB attr names).
        fill_nan        : Value to substitute for NaN numerics (default 0).
    """
    log.info(f"Starting EAV ingest — artefact_type_id={artefact_type_id}, artefact_id={artefact_id}")

    # 1. Load attribute map from DB
    attr_query = text(
        "SELECT attribute_name, id FROM artefacttypeattribute WHERE artefact_type_id = :type_id"
    )
    with engine.connect() as conn:
        attrs = pd.read_sql(attr_query, conn, params={"type_id": artefact_type_id})
    attr_map = dict(zip(attrs["attribute_name"], attrs["id"]))

    missing = [c for c in metrics_cols if c not in attr_map]
    if missing:
        log.warning(f"Skipping {len(missing)} unmapped columns: {missing}")

    valid_metrics = [c for c in metrics_cols if c in attr_map]
    if not valid_metrics:
        log.error("No valid metrics to ingest. Check artefacttypeattribute.")
        return

    df = df.copy()

    # 2. Keep only ts + valid columns, coerce all metric cols to numeric
    df_filtered = df[[ts_col] + valid_metrics].copy()
    df_filtered[ts_col] = pd.to_datetime(df_filtered[ts_col], errors="coerce")
    df_filtered = df_filtered.dropna(subset=[ts_col])
    df_filtered = df_filtered.drop_duplicates(subset=[ts_col], keep="last")

    for col in valid_metrics:
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors="coerce").fillna(fill_nan)

    # 3. Rename metric columns to their DB attribute IDs, then melt to long format
    rename_dict = {m: attr_map[m] for m in valid_metrics}
    df_filtered = df_filtered.rename(columns=rename_dict)
    attr_id_cols = list(rename_dict.values())

    log.info(f"Melting {len(df_filtered)} timestamp rows × {len(attr_id_cols)} attributes...")
    melted = df_filtered.melt(
        id_vars=[ts_col],
        value_vars=attr_id_cols,
        var_name="artefact_type_attribute_id",
        value_name="numeric_value",
    )
    melted = melted.dropna(subset=["numeric_value"])
    melted = melted.sort_values(by=ts_col).reset_index(drop=True)

    log.info(f"Total EAV rows to insert: {len(melted):,}")

    chunk_size = 50_000
    total_chunks = max(1, (len(melted) - 1) // chunk_size + 1)

    with engine.begin() as conn:
        for i in range(total_chunks):
            chunk = melted.iloc[i * chunk_size : (i + 1) * chunk_size]
            if chunk.empty:
                continue

            log.info(f"  Chunk {i+1}/{total_chunks} — {len(chunk):,} rows")

            # --- Insert artefactloginstance rows for new timestamps ---
            unique_ts = chunk[ts_col].drop_duplicates().tolist()
            ts_params = ", ".join([f"'{ts}'" for ts in unique_ts])

            existing_inst = pd.read_sql(
                text(
                    f"SELECT ts, id FROM artefactloginstance "
                    f"WHERE artefact_id = :aid AND ts IN ({ts_params})"
                ),
                conn,
                params={"aid": artefact_id},
            )
            existing_ts_set = set(existing_inst["ts"])

            new_ts = [ts for ts in unique_ts if ts not in existing_ts_set]
            if new_ts:
                # Only insert artefact_id + ts — all other cols are GENERATED ALWAYS
                inst_rows = [
                    {"artefact_id": artefact_id, "ts": ts} for ts in new_ts
                ]
                conn.execute(
                    text("""
                        INSERT INTO artefactloginstance (artefact_id, ts)
                        VALUES (:artefact_id, :ts)
                        ON CONFLICT (artefact_id, ts) DO NOTHING
                    """),
                    inst_rows,
                )
                # Refresh to get newly generated IDs
                existing_inst = pd.read_sql(
                    text(
                        f"SELECT ts, id FROM artefactloginstance "
                        f"WHERE artefact_id = :aid AND ts IN ({ts_params})"
                    ),
                    conn,
                    params={"aid": artefact_id},
                )

            # --- Map instance IDs onto the melted chunk ---
            inst_map = dict(zip(existing_inst["ts"], existing_inst["id"]))
            chunk_insert = chunk.copy()
            chunk_insert["artefact_log_instance_id"] = chunk_insert[ts_col].map(inst_map)
            chunk_insert = chunk_insert[
                ["artefact_log_instance_id", "artefact_type_attribute_id", "numeric_value"]
            ].dropna(subset=["artefact_log_instance_id"])

            # --- Bulk insert attribute values ---
            try:
                chunk_insert.to_sql(
                    "artefactlogattributevalue",
                    conn,
                    if_exists="append",
                    index=False,
                    method="multi",
                    chunksize=10_000,
                )
            except Exception as e:
                log.error(f"  Error inserting chunk {i+1}: {e}")

    log.info(f"Finished EAV ingest for artefact_type_id={artefact_type_id}")


# ---------------------------------------------------------------------------
# Per-source processors
# ---------------------------------------------------------------------------

def process_studer(engine):
    log.info("=== Processing Studer ===")
    studer_data = data_reader.read_studer_data_directory(
        "data/sample/studer/Studer_Oct2024_Aug_2025",
        return_raw_data=True,
        set_index=False,  # keep Timestamp as a plain column
    )

    # Timestamp column is not yet parsed when set_index=False
    studer_data["ts"] = pd.to_datetime(
        studer_data["Timestamp"], format="%d.%m.%Y %H:%M", dayfirst=True, errors="coerce"
    )

    col_mapping = {
        "Battery Voltage - L1": "battery_voltage_l1",
        "Battery Voltage - L2": "battery_voltage_l2",
        "Battery Voltage - L3": "battery_voltage_l3",
        "Grid Input Voltage - L1": "grid_input_voltage_l1",
        "Grid Input Voltage - L2": "grid_input_voltage_l2",
        "Grid Input Voltage - L3": "grid_input_voltage_l3",
        "Grid Input Current - L1": "grid_input_current_l1",
        "Grid Input Current - L2": "grid_input_current_l2",
        "Grid Input Current - L3": "grid_input_current_l3",
        "Apparent Power Output - L1": "apparent_power_output_l1",
        "Apparent Power Output - L2": "apparent_power_output_l2",
        "Apparent Power Output - L3": "apparent_power_output_l3",
        "Apparent Power Output w/ External - L1": "power_output_w_external_l1",
        "Apparent Power Output w/ External - L2": "power_output_w_external_l2",
        "Apparent Power Output w/ External - L3": "power_output_w_external_l3",
        "Studer Output Frequency - L1": "output_frequency_l1",
        "Studer Output Frequency - L2": "output_frequency_l2",
        "Studer Output Frequency - L3": "output_frequency_l3",
        "Grid Input Frequency - L1": "grid_input_frequency_l1",
        "Grid Input Frequency - L2": "grid_input_frequency_l2",
        "Grid Input Frequency - L3": "grid_input_frequency_l3",
        "XT-Phase - L1": "xt_phase_l1",
        "XT-Phase - L2": "xt_phase_l2",
        "XT-Phase - L3": "xt_phase_l3",
        "XT-Mode - L1": "xt_mode_l1",
        "XT-Mode - L2": "xt_mode_l2",
        "XT-Mode - L3": "xt_mode_l3",
        "Studer Grid Status - L1": "grid_status_l1",
        "Studer Grid Status - L2": "grid_status_l2",
        "Studer Grid Status - L3": "grid_status_l3",
        "XT-RME - L1": "xt_rme_l1",
        "XT-RME - L2": "xt_rme_l2",
        "XT-RME - L3": "xt_rme_l3",
        "XT-AUX1 - L1": "xt_aux1_l1",
        "XT-AUX1 - L2": "xt_aux1_l2",
        "XT-AUX1 - L3": "xt_aux1_l3",
        "XT-AUX2 - L1": "xt_aux2_l1",
        "XT-AUX2 - L2": "xt_aux2_l2",
        "XT-AUX2 - L3": "xt_aux2_l3",
        "Battery Voltage - L1-1": "battery_voltage_l1_1",
        "Battery Voltage - L2-2": "battery_voltage_l2_2",
        "Battery Voltage - L3-3": "battery_voltage_l3_3",
        "Battery Current - L1-1": "battery_current_l1",
        "Battery Current - L2-2": "battery_current_l2",
        "Battery Current - L3-3": "battery_current_l3",
        "Studer Grid Net Export/Import - L1-1": "studer_grid_imp_exp_l1",
        "Studer Grid Net Export/Import - L2-2": "studer_grid_imp_exp_l2",
        "Studer Grid Net Export/Import - L3-3": "studer_grid_imp_exp_l3",
        "Power Output - L1-1": "power_output_l1",
        "Power Output - L2-2": "power_output_l2",
        "Power Output - L3-3": "power_output_l3",
        "Studer Temperature - L1-1": "studer_temperature_l1",
        "Studer Temperature - L2-2": "studer_temperature_l2",
        "Studer Temperature - L3-3": "studer_temperature_l3",
        "Battery Voltage": "battery_voltage",
        "Battery Current": "battery_current",
        "Battery State of Charge": "battery_state_of_charge",
        "Battery Internal Temperature": "battery_temperature",
        "Solar Power": "solar_power",
        "Dev XT-DBG1": "xt_dbg1",
        "Dev BSP-locE": "bsp_loce",
        "Dev Sys MSG": "sys_msg",
        "Dev Sys SCOM Err": "sys_scom_err",
        "VT-PsoM - 1": "vt_psom_1",
        "VT-PsoM - All": "vt_psom_all",
        "VT-Mode": "vt_mode",
        "VT-Tp1M": "vt_tp1m",
        "VT-UpvM": "vt_upvm",
        "VT-IbaM": "vt_ibam",
        "VT-UbaM": "vt_ubam",
        "VT-Phas": "vt_phas",
        "VT-RME": "vt_rme",
        "VT-AUX1": "vt_aux_1",
        "VT-AUX2": "vt_aux_2",
    }

    studer_data = studer_data.rename(columns=col_mapping)
    log.info(f"Studer rows loaded: {len(studer_data):,}")
    ingest_to_eav(
        studer_data, engine,
        artefact_type_id=1, artefact_id=1,
        ts_col="ts", metrics_cols=list(col_mapping.values()),
    )


def process_enphase_gateway(engine):
    log.info("=== Processing Enphase Gateway (15-min) ===")
    df = data_reader.read_enphase_15min_data_file(
        "data/sample/enphase", "15mins_Oct_2024_Aug_2025.csv",
        set_index=True, format="%m/%d/%Y %H:%M",
    )
    df = df.reset_index()  # Date becomes a column
    df["ts"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.fillna(0)

    col_mapping = {
        "Energy Produced (Wh)": "energy_produced",
        "Energy Consumed (Wh)": "energy_consumed",
        "Exported to Grid (Wh)": "grid_exported",
        "Imported from Grid (Wh)": "grid_imported",
    }
    df = df.rename(columns=col_mapping)
    log.info(f"Enphase gateway rows loaded: {len(df):,}")
    ingest_to_eav(
        df, engine,
        artefact_type_id=2, artefact_id=2,
        ts_col="ts", metrics_cols=list(col_mapping.values()),
    )


def process_enphase_panels(engine):
    log.info("=== Processing Enphase Panel Production (daily) ===")
    panel_file = "data/sample/enphase/enphase_daily_Feb23_Sep24_module.csv"
    if not os.path.exists(panel_file):
        log.warning(f"Panel file not found: {panel_file}. Skipping.")
        return

    df = data_reader.read_enphase_panel_data_file(
        "data/sample/enphase", "enphase_daily_Feb23_Sep24_module.csv", set_index=True
    )
    df = df.reset_index()
    df["date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
    df = df.fillna(0)

    panel_cols = [c for c in df.columns if c not in ["Date", "Total", "date"]]

    insert_rows = []
    with engine.connect() as conn:
        for col in panel_cols:
            panel_id = conn.execute(
                text("SELECT id FROM panel WHERE model = :c"), {"c": col}
            ).scalar()
            if not panel_id:
                log.warning(f"No panel found for model '{col}' — run seed_metadata_v2.py first.")
                continue
            for _, row in df.iterrows():
                val = float(row[col])
                if val > 0:
                    insert_rows.append({
                        "site_id": 1,
                        "panel_id": panel_id,
                        "date": row["date"],
                        "production_wh": val,
                    })

    if insert_rows:
        insert_df = pd.DataFrame(insert_rows)
        with engine.begin() as conn:
            insert_df.to_sql(
                "panelproduction", conn, if_exists="append",
                index=False, method="multi", chunksize=2_000,
            )
        log.info(f"Inserted {len(insert_df):,} panel production rows.")
    else:
        log.warning("No panel production rows to insert.")


def _process_open_weather_file(engine, file_dir, file_name, artefact_id=3):
    """Helper to ingest one Open Weather CSV file into EAV."""
    file_path = os.path.join(file_dir, file_name)
    if not os.path.exists(file_path):
        log.warning(f"File not found: {file_path}. Skipping.")
        return

    log.info(f"  Loading {file_name} ...")
    df = data_reader.read_open_weather_data_file(
        file_dir, file_name, set_index=False, filter_columns=False
    )
    if "dt_iso" in df.columns:
        df.drop(columns=["dt_iso"], inplace=True)

    df["ts"] = pd.to_datetime(df["dt"], unit="s", errors="coerce")
    df = df.fillna(0)

    # Text columns not stored in EAV (numeric_value only) — exclude them
    col_mapping = {
        "timezone": "timezone",
        "lat": "latitude",
        "lon": "longitude",
        "temp": "temperature",
        "visibility": "visibility",
        "dew_point": "dew_point",
        "feels_like": "feels_like_temperature",
        "temp_min": "temperature_min",
        "temp_max": "temperature_max",
        "pressure": "pressure",
        "sea_level": "sea_level",
        "grnd_level": "ground_level",
        "humidity": "humidity",
        "wind_speed": "wind_speed",
        "wind_deg": "wind_degree",
        "wind_gust": "wind_gust",
        "rain_1h": "rain_1h",
        "rain_3h": "rain_3h",
        "snow_1h": "snow_1h",
        "snow_3h": "snow_3h",
        "clouds_all": "clouds_all",
        "weather_id": "weather_id",
    }
    df = df.rename(columns=col_mapping)
    log.info(f"  Rows loaded: {len(df):,}")
    ingest_to_eav(
        df, engine,
        artefact_type_id=4, artefact_id=artefact_id,
        ts_col="ts", metrics_cols=list(col_mapping.values()),
    )


def process_open_weather(engine):
    log.info("=== Processing Open Weather ===")
    ow_dir = "data/sample/weather/open_weather"
    # Ingest all CSV files in the directory
    import glob
    files = glob.glob(os.path.join(ow_dir, "*.csv")) + glob.glob(os.path.join(ow_dir, "*.CSV"))
    if not files:
        log.warning(f"No Open Weather CSV files found in {ow_dir}.")
        return
    for f in files:
        _process_open_weather_file(engine, ow_dir, os.path.basename(f))


def process_kaatru_weather(engine):
    log.info("=== Processing Kaatru Weather ===")

    with engine.connect() as conn:
        artefact_id = conn.execute(
            text("SELECT id FROM artefact WHERE artefact_type_id = 3")
        ).scalar()
    if not artefact_id:
        log.error("Kaatru artefact not found in DB. Run seed_metadata_v2.py first.")
        return

    df = data_reader.read_weather_kaatru_data_directory("data/sample/weather/kaatru")
    df = df.reset_index()

    # Handle the `value.sNoxI` mixed-type column (can contain strings)
    if "value.sNoxI" in df.columns:
        df["value.sNoxI"] = pd.to_numeric(df["value.sNoxI"], errors="coerce")

    df["ts"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df.fillna(0)

    col_mapping = {
        "value.lat": "latitude",
        "value.lon": "longitude",
        "value.alt": "altitude",
        "value.sog": "speed_over_ground",
        "value.cog": "course_over_ground",
        "value.hdop": "horizontal_dilution_precision",
        "value.ax": "acceleration_x",
        "value.ay": "acceleration_y",
        "value.az": "acceleration_z",
        "value.gx": "gyro_x",
        "value.gy": "gyro_y",
        "value.gz": "gyro_z",
        "value.accTemp": "accelerometer_temp",
        "value.pIDar": "packetID_arduino",
        "value.aUT": "arduino_uptime",
        "value.temp": "temperature",
        "value.rh": "relative_humidity",
        "value.wSpeed": "wind_speed",
        "value.rain": "rain",
        "value.sPM1": "pm1",
        "value.sPM2": "pm2",
        "value.sPM4": "pm4",
        "value.sPM10": "pm10",
        "value.sNPMp5": "npm_p5",
        "value.sNPM1": "npm_1",
        "value.sNPM2": "npm_2",
        "value.sNPM4": "npm_4",
        "value.sNPM10": "npm_10",
        "value.sTPS": "typical_partical_size",
        "value.sTemp": "temperature_sen55",
        "value.sRh": "relative_humidity_sen55",
        "value.sVocI": "volatile_organic_compound",
        "value.sNoxI": "nox_compounds",
        "value.aTd0": "sunlight_sensor_1_light",
        "value.aTd1": "sunlight_sensor_2_ir",
        "value.aTd2": "sunlight_sensor_3_uv",
        "value.a12V": "input_voltage",
        "value.aFanTacho": "fan_tachometer",
        "value.pidState": "pid_state",
        "value.BuzzerState": "buzzer_state",
        "value.setpoint": "setpoint",
        "value.FanPWM": "fan_pwm",
        "value.minRpm": "min_rpm",
        "value.maxRpm": "max_rpm",
    }
    df = df.rename(columns=col_mapping)
    log.info(f"Kaatru rows loaded: {len(df):,}")
    ingest_to_eav(
        df, engine,
        artefact_type_id=3, artefact_id=artefact_id,
        ts_col="ts", metrics_cols=list(col_mapping.values()),
    )


# ---------------------------------------------------------------------------
# Verification helper
# ---------------------------------------------------------------------------
def verify_counts(engine):
    log.info("=== Verification Counts ===")
    with engine.connect() as conn:
        result = pd.read_sql(
            text("""
                SELECT
                    at.name AS source,
                    COUNT(DISTINCT ali.id) AS log_instances,
                    COUNT(alav.id) AS attribute_values
                FROM artefacttype at
                JOIN artefact a ON a.artefact_type_id = at.id
                JOIN artefactloginstance ali ON ali.artefact_id = a.id
                JOIN artefactlogattributevalue alav ON alav.artefact_log_instance_id = ali.id
                GROUP BY at.name
                ORDER BY at.name
            """),
            conn,
        )
    if result.empty:
        log.warning("No data found in EAV tables!")
    else:
        log.info("\n" + result.to_string(index=False))

    with engine.connect() as conn:
        panel_count = conn.execute(text("SELECT COUNT(*) FROM panelproduction")).scalar()
    log.info(f"panelproduction rows: {panel_count:,}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    engine = get_engine("circa_test")  # swap "circa_test" → "circa" for production

    process_studer(engine)
    process_enphase_gateway(engine)
    process_enphase_panels(engine)
    process_open_weather(engine)
    process_kaatru_weather(engine)

    verify_counts(engine)
    log.info("All backfills complete!")
