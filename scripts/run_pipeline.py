"""
One-shot pipeline runner for the V2 data ingestion.

Usage:
    # Test against circa_test (safe — does NOT touch production):
    conda activate dev
    python scripts/run_pipeline.py

    # Run against production (use with caution):
    python scripts/run_pipeline.py --db circa

Steps executed in order:
  1. setup_test_db  — clone circa schema into circa_test (test mode only)
  2. seed_metadata  — insert Kaatru attrs + panel metadata
  3. backfill_data  — ingest all CSVs into EAV tables
  4. verify_counts  — print row counts per source as a sanity check
"""

import sys
import os
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

sys.path.append(os.path.abspath("src"))


def main():
    parser = argparse.ArgumentParser(description="CIRCA V2 Ingestion Pipeline")
    parser.add_argument(
        "--db",
        default="circa_test",
        help="Target database name (default: circa_test). Use 'circa' for production.",
    )
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Skip setup_test_db step (use if circa_test already exists).",
    )
    parser.add_argument(
        "--skip-seed",
        action="store_true",
        help="Skip seed_metadata step (use if metadata was already seeded).",
    )
    parser.add_argument(
        "--only",
        choices=["studer", "enphase_gateway", "enphase_panels", "open_weather", "kaatru"],
        default=None,
        help="Run only a single source processor.",
    )
    args = parser.parse_args()

    db_name = args.db
    log.info(f"Target database: {db_name}")

    # ------------------------------------------------------------------
    # Step 1 — Setup test DB (only when targeting circa_test)
    # ------------------------------------------------------------------
    if db_name == "circa_test" and not args.skip_setup:
        log.info("Step 1/3 — Setting up test database...")
        from scripts.setup_test_db import setup_test_db
        setup_test_db()
    else:
        log.info("Step 1/3 — Skipping database setup.")

    # ------------------------------------------------------------------
    # Step 2 — Seed metadata
    # ------------------------------------------------------------------
    if not args.skip_seed:
        log.info("Step 2/3 — Seeding metadata...")
        from sqlalchemy import create_engine
        engine = create_engine(
            f"postgresql+psycopg2://postgres:root@127.0.0.1:5432/{db_name}"
        )
        from scripts.seed_metadata_v2 import seed_kaatru_metadata, seed_panel_metadata
        seed_kaatru_metadata(engine)
        seed_panel_metadata(engine)
    else:
        log.info("Step 2/3 — Skipping metadata seeding.")

    # ------------------------------------------------------------------
    # Step 3 — Ingest data
    # ------------------------------------------------------------------
    log.info("Step 3/3 — Ingesting data...")
    from sqlalchemy import create_engine
    engine = create_engine(
        f"postgresql+psycopg2://postgres:root@127.0.0.1:5432/{db_name}"
    )

    import scripts.backfill_data_v2 as pipeline

    if args.only:
        processors = {
            "studer": pipeline.process_studer,
            "enphase_gateway": pipeline.process_enphase_gateway,
            "enphase_panels": pipeline.process_enphase_panels,
            "open_weather": pipeline.process_open_weather,
            "kaatru": pipeline.process_kaatru_weather,
        }
        processors[args.only](engine)
    else:
        pipeline.process_studer(engine)
        pipeline.process_enphase_gateway(engine)
        pipeline.process_enphase_panels(engine)
        pipeline.process_open_weather(engine)
        pipeline.process_kaatru_weather(engine)

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------
    pipeline.verify_counts(engine)
    log.info("Pipeline complete!")


if __name__ == "__main__":
    main()
