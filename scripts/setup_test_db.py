"""
Creates and initialises the circa_test database for safe V2 pipeline testing.

Steps:
  1. Drop and recreate circa_test
  2. Restore the full schema + reference/metadata data from circa
  3. Truncate all time-series tables so ingestion starts from a clean slate

Production data in `circa` is NEVER modified.
"""

import subprocess
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config — adjust if your Postgres credentials differ
# ---------------------------------------------------------------------------
PG_USER = "postgres"
PG_HOST = "localhost"
PG_PASSWORD = "root"
SOURCE_DB = "circa"
TEST_DB = "circa_test"
DUMP_FILE = "schema_and_data.sql"

# Tables that hold time-series data — will be emptied in the test DB.
# These are the only tables the V2 pipeline writes to.
TIME_SERIES_TABLES = [
    "artefactlogattributevalue",   # must come before artefactloginstance (FK)
    "artefactloginstance",
    "panelproduction",
]


def run(cmd: list, env: dict, check=True) -> subprocess.CompletedProcess:
    log.debug("Running: " + " ".join(cmd))
    return subprocess.run(cmd, env=env, check=check, capture_output=False)


def setup_test_db():
    env = os.environ.copy()
    env["PGPASSWORD"] = PG_PASSWORD

    base_args = ["-U", PG_USER, "-h", PG_HOST]

    # 1. Drop and recreate test DB
    log.info(f"Dropping '{TEST_DB}' if it exists...")
    run(["psql"] + base_args + ["-c", f"DROP DATABASE IF EXISTS {TEST_DB};"], env=env)

    log.info(f"Creating '{TEST_DB}'...")
    run(["psql"] + base_args + ["-c", f"CREATE DATABASE {TEST_DB};"], env=env)

    # 2. Dump source DB (schema + reference data only — no time-series rows needed,
    #    but it's simpler to dump everything and then truncate)
    log.info(f"Dumping '{SOURCE_DB}' to {DUMP_FILE} ...")
    run(["pg_dump"] + base_args + ["-f", DUMP_FILE, SOURCE_DB], env=env)

    # 3. Restore into test DB
    log.info(f"Restoring into '{TEST_DB}'...")
    run(["psql"] + base_args + ["-d", TEST_DB, "-f", DUMP_FILE], env=env)

    # 4. Truncate time-series tables so the test DB starts empty for ingestion
    log.info("Truncating time-series tables in test DB...")
    truncate_sql = "; ".join(
        [f"TRUNCATE TABLE {t} CASCADE" for t in TIME_SERIES_TABLES]
    ) + ";"
    run(["psql"] + base_args + ["-d", TEST_DB, "-c", truncate_sql], env=env)

    # 5. Cleanup dump file
    if os.path.exists(DUMP_FILE):
        os.remove(DUMP_FILE)
        log.info(f"Removed {DUMP_FILE}")

    log.info(
        f"Done — '{TEST_DB}' is ready with all metadata but empty time-series tables."
    )


if __name__ == "__main__":
    setup_test_db()
