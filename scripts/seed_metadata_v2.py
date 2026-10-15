"""
Metadata seeder for V2 pipeline.
Must be run AFTER setup_test_db.py and BEFORE backfill_data_v2.py.

Seeds:
  - Kaatru Weather artefact + all artefacttypeattribute rows
  - Enphase panelgroup + panel rows (discovered from the panel CSV columns)
"""

import sys
import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.append(os.path.abspath("src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def get_engine(db_name="circa_test"):
    return create_engine(
        f"postgresql+psycopg2://postgres:root@127.0.0.1:5432/{db_name}"
    )


# ---------------------------------------------------------------------------
# Kaatru metadata
# ---------------------------------------------------------------------------

KAATRU_ATTRS = [
    ("latitude", "number"),
    ("longitude", "number"),
    ("altitude", "number"),
    ("speed_over_ground", "number"),
    ("course_over_ground", "number"),
    ("horizontal_dilution_precision", "number"),
    ("acceleration_x", "number"),
    ("acceleration_y", "number"),
    ("acceleration_z", "number"),
    ("gyro_x", "number"),
    ("gyro_y", "number"),
    ("gyro_z", "number"),
    ("accelerometer_temp", "number"),
    ("packetID_arduino", "number"),
    ("arduino_uptime", "number"),
    ("temperature", "number"),
    ("relative_humidity", "number"),
    ("wind_speed", "number"),
    ("rain", "number"),
    ("pm1", "number"),
    ("pm2", "number"),
    ("pm4", "number"),
    ("pm10", "number"),
    ("npm_p5", "number"),
    ("npm_1", "number"),
    ("npm_2", "number"),
    ("npm_4", "number"),
    ("npm_10", "number"),
    ("typical_partical_size", "number"),
    ("temperature_sen55", "number"),
    ("relative_humidity_sen55", "number"),
    ("volatile_organic_compound", "number"),
    ("nox_compounds", "number"),
    ("sunlight_sensor_1_light", "number"),
    ("sunlight_sensor_2_ir", "number"),
    ("sunlight_sensor_3_uv", "number"),
    ("input_voltage", "number"),
    ("fan_tachometer", "number"),
    ("pid_state", "number"),
    ("buzzer_state", "number"),
    ("setpoint", "number"),
    ("fan_pwm", "number"),
    ("min_rpm", "number"),
    ("max_rpm", "number"),
]


def seed_kaatru_metadata(engine):
    log.info("Seeding Kaatru Weather metadata...")
    with engine.begin() as conn:
        # Ensure artefacttype=3 (WEATHER_STATION) exists
        wt = conn.execute(
            text("SELECT id FROM artefacttype WHERE id = 3")
        ).fetchone()
        if not wt:
            log.error(
                "artefacttype id=3 (WEATHER_STATION) not found — "
                "did setup_test_db.py run correctly?"
            )
            return

        # Insert artefact if missing
        res = conn.execute(
            text("SELECT id FROM artefact WHERE artefact_type_id = 3")
        ).fetchone()
        if not res:
            conn.execute(text("""
                INSERT INTO artefact (site_id, artefact_type_id, artefact_code, display_name)
                VALUES (1, 3, 'KAATRU_001', 'Kaatru Weather Station - FormulaHouse')
            """))
            log.info("Inserted Kaatru artefact.")
        else:
            log.info("Kaatru artefact already exists.")

        # Upsert attributes
        existing = {
            r[0]
            for r in conn.execute(
                text("SELECT attribute_name FROM artefacttypeattribute WHERE artefact_type_id = 3")
            ).fetchall()
        }
        inserted = 0
        for attr, dtype in KAATRU_ATTRS:
            if attr not in existing:
                conn.execute(text("""
                    INSERT INTO artefacttypeattribute (artefact_type_id, attribute_name, data_type)
                    VALUES (3, :attr, :dtype)
                """), {"attr": attr, "dtype": dtype})
                inserted += 1
        log.info(f"Kaatru attributes: {inserted} inserted, {len(existing)} already present.")


# ---------------------------------------------------------------------------
# Enphase panel metadata
# ---------------------------------------------------------------------------

def seed_panel_metadata(engine):
    log.info("Seeding Enphase Panel metadata...")
    import utils.data_reader_csv as data_reader

    panel_file = "data/sample/enphase/enphase_daily_Feb23_Sep24_module.csv"
    if not os.path.exists(panel_file):
        log.warning(f"Panel file not found: {panel_file}. Skipping.")
        return

    df = data_reader.read_enphase_panel_data_file(
        "data/sample/enphase", "enphase_daily_Feb23_Sep24_module.csv", set_index=True
    )
    df = df.reset_index()

    # Panel column format: <serial>_<groupName>  e.g. 122216033790_C
    panel_cols = [c for c in df.columns if c not in ("Date", "Total")]
    log.info(f"Found {len(panel_cols)} panel columns.")

    with engine.begin() as conn:
        # Discover distinct groups from column names
        groups = {}
        for col in panel_cols:
            parts = col.split("_")
            if len(parts) >= 2:
                grp_name = parts[-1]  # last part = group letter e.g. 'C'
                if grp_name not in groups:
                    existing_grp = conn.execute(
                        text("SELECT id FROM panelgroup WHERE name = :g AND site_id = 1"),
                        {"g": grp_name},
                    ).scalar()
                    if not existing_grp:
                        res = conn.execute(
                            text(
                                "INSERT INTO panelgroup (site_id, name) VALUES (1, :g) RETURNING id"
                            ),
                            {"g": grp_name},
                        )
                        groups[grp_name] = res.scalar()
                        log.info(f"  Inserted panelgroup '{grp_name}'.")
                    else:
                        groups[grp_name] = existing_grp

        # Insert panel rows — use model as the natural unique key
        for col in panel_cols:
            parts = col.split("_")
            if len(parts) < 2:
                continue
            grp_name = parts[-1]
            grp_id = groups.get(grp_name)

            existing_panel = conn.execute(
                text("SELECT id FROM panel WHERE model = :model AND site_id = 1"),
                {"model": col},
            ).scalar()
            if not existing_panel:
                conn.execute(text("""
                    INSERT INTO panel (site_id, group_id, model, capacity_w)
                    VALUES (1, :grp_id, :model, 300)
                """), {"grp_id": grp_id, "model": col})
                log.info(f"  Inserted panel '{col}' (group={grp_name}).")
            else:
                log.debug(f"  Panel '{col}' already exists.")

    log.info("Panel metadata seeding complete.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    engine = get_engine("circa_test")  # swap to "circa" for production
    seed_kaatru_metadata(engine)
    seed_panel_metadata(engine)
    log.info("Metadata seeding complete.")
