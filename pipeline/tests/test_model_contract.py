"""The semantic model reads only contract tables, and only columns the gold tables really have."""
import re
from pathlib import Path

import pyarrow.parquet as pq

from retail_pipeline.build import GOLD_TABLES

MODEL_TABLES = Path(__file__).resolve().parents[2] / "fabric/StorePerformance.SemanticModel/definition/tables"
# lakehouse tables marked "Used by: Model" in docs/architecture.md
MODEL_SOURCES = {"dim_date", "dim_store", "dim_item", "fact_sales", "fact_store_day", "fact_stockout_risk", "user_access"}


def lakehouse_reads() -> list[tuple[str, str, list[str]]]:
    """(tmdl file, lakehouse table, columns its partition selects) for every table read from the lakehouse."""
    reads = []
    for path in sorted(MODEL_TABLES.glob("*.tmdl")):
        text = path.read_text(encoding="utf-8")
        table = re.search(r'Item = "(\w+)"', text)
        if table:
            selected = re.search(r"Table\.SelectColumns\(\w+, \{([^}]*)\}\)", text)
            assert selected, f"{path.name}: the partition must pick its columns with Table.SelectColumns"
            reads.append((path.name, table.group(1), re.findall(r'"(\w+)"', selected.group(1))))
    return reads


def test_model_reads_only_contract_tables():
    tables = {table for _, table, _ in lakehouse_reads()}
    assert tables and tables <= MODEL_SOURCES


def test_model_columns_exist_in_gold_tables(full_build):
    cfg, _ = full_build
    for name, table, columns in lakehouse_reads():
        if table in GOLD_TABLES:
            available = set(pq.read_schema(cfg.out_dir / "gold" / f"{table}.parquet").names)
            assert set(columns) <= available, f"{name}: {set(columns) - available}"


# Gold tables the Databricks project (favorita-stockout-promo-databricks) publishes for this model, with every
# column it guarantees. See docs/architecture.md, "Databricks source".
DATABRICKS_SOURCES = {
    "fact_stockout_run": {"store_key", "item_key", "start_date_key", "end_date_key", "run_days", "spine_days",
                          "calendar_days", "lambda_units", "dispersion", "p_value", "p_poisson",
                          "expected_lost_units", "is_flagged"},
    "stockout_store_week": {"store_key", "city", "week_start", "week_start_key", "item_days", "flagged_days", "rate"},
    "fact_promo_event": {"store_key", "item_key", "family", "start_date_key", "end_date_key", "promo_days",
                         "promo_units", "baseline_units", "uplift", "post_units", "post_expected_units", "post_dip",
                         "net_lift", "touches_payday_or_holiday"},
    "promo_family_summary": {"family", "n_events", "uplift_median", "uplift_lo", "uplift_hi", "n_dip_events",
                             "dip_median", "dip_lo", "dip_hi", "n_net_events", "net_median", "net_lo", "net_hi"},
    "stockout_bh_summary": {"tested_runs", "flagged_runs", "bh_cutoff", "max_chance_flags", "poisson_flagged_runs"},
}


def databricks_reads() -> list[tuple[str, str, list[str]]]:
    """(tmdl file, Databricks gold table, columns its partition selects) for every table read from Databricks."""
    reads = []
    for path in sorted(MODEL_TABLES.glob("*.tmdl")):
        text = path.read_text(encoding="utf-8")
        table = re.search(r'Name = "(\w+)", Kind = "Table"', text)
        if table:
            assert "Databricks.Catalogs(DatabricksHost, DatabricksHttpPath" in text, f"{path.name}: use the parameters"
            selected = re.search(r"Table\.SelectColumns\(\w+, \{([^}]*)\}\)", text)
            assert selected, f"{path.name}: the partition must pick its columns with Table.SelectColumns"
            reads.append((path.name, table.group(1), re.findall(r'"(\w+)"', selected.group(1))))
    return reads


def test_model_reads_only_documented_databricks_tables():
    reads = databricks_reads()
    assert {table for _, table, _ in reads} == set(DATABRICKS_SOURCES)
    for name, table, columns in reads:
        assert set(columns) <= DATABRICKS_SOURCES[table], f"{name}: {set(columns) - DATABRICKS_SOURCES[table]}"
