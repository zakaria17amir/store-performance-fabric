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
