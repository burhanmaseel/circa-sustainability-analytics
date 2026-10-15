# CIRCA Sustainability Analytics

A comprehensive sustainability analytics platform that ingests, processes, and visualises energy and weather data from multiple sources — Studer inverters, Enphase solar gateways, Open Weather API, and Kaatru IoT weather stations.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Database Setup](#database-setup)
5. [Data Ingestion](#data-ingestion)
   - [Legacy Pipeline (v1)](#legacy-pipeline-v1)
   - [V2 Pipeline (PostgreSQL EAV)](#v2-pipeline-postgresql-eav)
6. [Running the Streamlit Dashboard](#running-the-streamlit-dashboard)
7. [Available Dashboards](#available-dashboards)
8. [Project Architecture](#project-architecture)
9. [Data Sources & CSV Format](#data-sources--csv-format)
10. [Troubleshooting](#troubleshooting)

---

## Project Structure

```
circa-sustainability-analytics/
├── data/
│   ├── sample/                     # Source CSV data files
│   │   ├── enphase/                # Enphase 15-min gateway & panel CSVs
│   │   ├── studer/                 # Studer inverter CSVs (by date folder)
│   │   └── weather/
│   │       ├── open_weather/       # Open Weather API CSV exports
│   │       └── kaatru/             # Kaatru IoT station JSON/CSV files
│   ├── processed/                  # Post-processing outputs
│   └── raw/                        # Raw unprocessed files
├── scripts/
│   ├── backfill_data.py            # Legacy MySQL ingestion script (DO NOT MODIFY)
│   ├── backfill_data_v2.py         # V2 PostgreSQL EAV ingestion pipeline
│   ├── seed_metadata_v2.py         # Seeds artefact metadata before V2 ingestion
│   ├── setup_test_db.py            # Creates & populates a safe test DB (circa_test)
│   └── test_db_connection.py       # Quick DB connectivity check
├── src/
│   ├── db/
│   │   └── connection.py           # SQLAlchemy engine & psycopg2 connection helpers
│   └── utils/
│       ├── data_reader.py          # DB-backed data reader (used by dashboards)
│       ├── data_reader_csv.py      # CSV-backed data reader (used by ingestion)
│       ├── grid_metrics.py         # Grid metric calculation helpers
│       ├── weather_data.py         # Weather stat calculation helpers
│       └── streamlit_visualization.py
├── streamlit_app/
│   ├── app.py                      # Main Streamlit entrypoint
│   └── pages/
│       ├── enphase_dashboard.py
│       ├── grid_metrics_dashboard.py
│       ├── open_weather_dashboard.py
│       ├── kaatru_weather_dashboard.py
│       ├── enphase/                # Enphase visualisation modules
│       ├── open_weather/           # Open Weather visualisation modules
│       ├── kaatru_weather/         # Kaatru visualisation modules
│       └── studer/                 # Studer visualisation modules
├── notebooks/                      # Jupyter exploration notebooks
├── docs/                           # ERD, case studies, and schema docs
├── pyproject.toml
├── requirements.txt
└── .env                            # Local environment variables (not committed)
```

---

## Prerequisites

- **Python 3.10+**
- **Conda** (recommended) or `venv`
- **PostgreSQL 14+** running locally
- **`pg_dump` / `psql`** available on your PATH (comes with PostgreSQL)

---

## Environment Setup

### 1. Create and activate the Conda environment

```bash
conda create -n dev python=3.10 -y
conda activate dev
```

### 2. Install the package and its dependencies

```bash
pip install -e .
pip install -r requirements.txt
```

> `pip install -e .` installs the `src/` package in editable mode so that all imports like `from db.connection import ...` resolve correctly.

### 3. Configure the `.env` file

Create a `.env` file in the project root (it is gitignored):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=circa
DB_USER=postgres
DB_PASSWORD=your_password
```

> **Important:** The Streamlit app and dashboard scripts read these variables automatically via `python-dotenv`.

### 4. Verify the database connection

```bash
conda activate dev
python scripts/test_db_connection.py
```

---

## Database Setup

### Production Database (`circa`)

The production database must already exist with the full schema applied. The schema is documented in `docs/ERD.pgerd`.

Key tables used by this project:

| Table | Purpose |
|---|---|
| `artefacttype` | Lookup: Studer, Enphase, Open Weather, Kaatru |
| `artefact` | One row per physical device/feed |
| `artefacttypeattribute` | Attribute definitions (e.g., `temperature`, `battery_voltage`) |
| `artefactloginstance` | One row per timestamp per artefact |
| `artefactlogattributevalue` | EAV values — the main time-series store |
| `panel` / `panelgroup` | Enphase panel metadata |
| `panelproduction` | Daily panel production |
| `open_weather` | Flat legacy table for Open Weather (still used by temperature viz) |

### Test Database (`circa_test`)

To safely test ingestion **without touching production data**, create a test DB:

```bash
conda activate dev
python scripts/setup_test_db.py
```

This script will:
1. Drop `circa_test` if it exists.
2. Create a fresh `circa_test`.
3. Dump the full `circa` database (schema + reference/metadata data).
4. Restore it into `circa_test`.
5. Truncate all time-series tables (`artefactloginstance`, `artefactlogattributevalue`, `panelproduction`) so production data is not duplicated.

> ⚠️ **Never run ingestion scripts against `circa` directly until you have validated on `circa_test`.**

---

## Data Ingestion

### CSV File Layout

Place all source CSV files in `data/sample/` using this structure:

```
data/sample/
├── enphase/
│   ├── 15mins_Oct_2024_Aug_2025.csv          # Gateway 15-min energy data
│   └── enphase_daily_Feb23_Sep24_module.csv  # Per-panel daily production
├── studer/
│   └── Studer_Oct2024_Aug_2025/              # Folder of daily Studer CSVs
├── weather/
│   ├── open_weather/
│   │   └── FormulaHouse-Jan2023-Sep2024.csv
│   └── kaatru/                               # Folder of Kaatru JSON/CSV files
```

---

### Legacy Pipeline (v1)

> ⛔ **Do not modify `scripts/backfill_data.py`.** It targets a MySQL database and is kept for historical reference only.

```bash
# Only run if you have the original MySQL circa database
python scripts/backfill_data.py
```

---

### V2 Pipeline (PostgreSQL EAV)

The V2 pipeline ingests all CSV data into the normalised PostgreSQL EAV schema. It is split into two steps: metadata seeding and data ingestion.

#### Step 1 — Set up the test database

```bash
conda activate dev
python scripts/setup_test_db.py
```

#### Step 2 — Seed artefact metadata

This script inserts:
- A new `artefact` row for the **Kaatru Weather Station** (artefact_type_id=3)
- All Kaatru attribute definitions into `artefacttypeattribute`
- Panel groups and panel rows from the Enphase module CSV

```bash
conda activate dev
python scripts/seed_metadata_v2.py
```

#### Step 3 — Run the V2 ingestion

```bash
conda activate dev
python scripts/backfill_data_v2.py
```

This will process all data sources in order:

| Source | Script Function | Target Tables |
|---|---|---|
| Studer Inverter | `process_studer()` | `artefactloginstance`, `artefactlogattributevalue` |
| Enphase Gateway (15-min) | `process_enphase_gateway()` | `artefactloginstance`, `artefactlogattributevalue` |
| Enphase Panels (daily) | `process_enphase_panels()` | `panelproduction` |
| Open Weather | `process_open_weather()` | `artefactloginstance`, `artefactlogattributevalue` |
| Kaatru Weather Station | `process_kaatru_weather()` | `artefactloginstance`, `artefactlogattributevalue` |

> By default `backfill_data_v2.py` targets **`circa_test`**. To switch to production, change `get_test_engine()` or pass the production connection string.

#### How the EAV ingestion works

1. Reads the attribute map from `artefacttypeattribute` for the target `artefact_type_id`.
2. Renames CSV columns to match the DB attribute names.
3. Melts the wide DataFrame into long EAV format (one row per `timestamp × attribute`).
4. Batch-inserts `artefactloginstance` rows (one per unique timestamp), skipping any that already exist.
5. Bulk-inserts `artefactlogattributevalue` rows in chunks of 50,000 for performance.
6. Duplicate timestamps in the CSV are automatically deduplicated (last value wins).

---

## Running the Streamlit Dashboard

```bash
conda activate dev
cd streamlit_app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

> **Note:** Run `streamlit run app.py` from inside the `streamlit_app/` directory so that page imports resolve correctly.

---

## Available Dashboards

| Dashboard | Description |
|---|---|
| **Home** | Overview of the platform and available dashboards |
| **Grid Metric Dashboard** | Studer inverter grid import/export, battery SOC, and power metrics |
| **Enphase Dashboard** | Energy produced, consumed, and grid import/export from the Enphase gateway |
| **Open Weather Dashboard** | Hourly weather conditions: temperature, wind, humidity, clouds, dew point, pressure |
| **Kaatru Weather Dashboard** | IoT station metrics: particulate matter, NOx, VOC, UV, wind, temperature, humidity |

Each dashboard is backed by live queries to the `circa` PostgreSQL database.

---

## Project Architecture

```
CSV Files
    │
    ▼
data_reader_csv.py          ← Parses and cleans raw CSV data
    │
    ▼
backfill_data_v2.py         ← Maps columns → EAV, bulk-inserts in chunks
    │
    ▼
PostgreSQL (circa / circa_test)
    │  artefactloginstance
    │  artefactlogattributevalue
    │  panelproduction
    ▼
data_reader.py              ← DB-backed queries used by Streamlit pages
    │
    ▼
Streamlit Dashboards        ← Visualisation layer
```

---

## Data Sources & CSV Format

### Studer Inverter
- **Directory:** `data/sample/studer/<folder>/`
- **Format:** Multiple CSV files, one per day. Columns include `Timestamp`, `Battery Voltage - L1`, `Solar Power`, `Battery State of Charge`, etc.

### Enphase Gateway (15-min)
- **File:** `data/sample/enphase/15mins_Oct_2024_Aug_2025.csv`
- **Columns:** `Date`, `Energy Produced (Wh)`, `Energy Consumed (Wh)`, `Exported to Grid (Wh)`, `Imported from Grid (Wh)`

### Enphase Panels (daily)
- **File:** `data/sample/enphase/enphase_daily_Feb23_Sep24_module.csv`
- **Columns:** `Date`, `Total`, and one column per panel (e.g., `122216033790_C`)

### Open Weather
- **File:** `data/sample/weather/open_weather/FormulaHouse-Jan2023-Sep2024.csv`
- **Columns:** UNIX timestamp (`dt`), `lat`, `lon`, `temp`, `feels_like`, `humidity`, `wind_speed`, `clouds_all`, etc.

### Kaatru Weather Station
- **Directory:** `data/sample/weather/kaatru/`
- **Format:** JSON/CSV files with nested `value.*` keys for sensor readings (PM1/2/4/10, NOx, VOC, GPS, accelerometer, temperature, etc.)

---

## Troubleshooting

### `ModuleNotFoundError` when running scripts

Make sure the package is installed in editable mode and you are using the correct environment:

```bash
conda activate dev
pip install -e .
```

### `FATAL: database "circa" does not exist`

Check that PostgreSQL is running and the `.env` values are correct:

```bash
psql -U postgres -h localhost -c "\l"
```

### Streamlit: `streamlit: command not found`

```bash
conda activate dev
pip install streamlit
```

### Dashboard shows "No data available"

1. Verify the database has data:
   ```bash
   conda activate dev
   python scripts/test_db_connection.py
   ```
2. Run the V2 pipeline against `circa_test` first to confirm ingestion works.
3. Check that `.env` points to the correct database (`DB_NAME=circa`).

### `pg_dump` / `psql` not found on Windows

Add the PostgreSQL `bin` directory to your system PATH, e.g.:
```
C:\Program Files\PostgreSQL\16\bin
```