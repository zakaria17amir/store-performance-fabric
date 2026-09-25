import shutil
from pathlib import Path
from string import Template

import duckdb

from .checks import run_checks
from .config import BuildConfig

SQL_DIR = Path(__file__).parent / "sql"
STAGES = ("bronze", "silver", "gold")
GOLD_TABLES = ("dim_date", "stg_store", "stg_item", "stg_store_day", "fact_sales", "fact_stockout_risk")


def sql_params(cfg: BuildConfig) -> dict[str, str]:
    return {
        "raw_dir": cfg.raw_dir.resolve().as_posix(),
        "sample": "true" if cfg.sample else "false",
        "start_date": cfg.start_date.isoformat(),
        "stockout_from": cfg.stockout_from.isoformat(),
        "lookback_days": str(cfg.lookback_days),
        "min_expected_units": str(cfg.min_expected_units),
        "min_receipts_share": str(cfg.min_receipts_share),
        "post_promo_days": str(cfg.post_promo_days),
    }


def run_stages(con: duckdb.DuckDBPyConnection, cfg: BuildConfig, stages=STAGES) -> None:
    """Run every SQL file of each stage in file-name order. One statement per file."""
    params = sql_params(cfg)
    for stage in stages:
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {stage}")
        for path in sorted((SQL_DIR / stage).glob("*.sql")):
            con.execute(Template(path.read_text(encoding="utf-8")).substitute(params))


class DataCheckError(RuntimeError):
    def __init__(self, failures: dict[str, int]):
        super().__init__("Data checks failed: " + ", ".join(f"{k}={v}" for k, v in failures.items()))
        self.failures = failures


def export_gold(con: duckdb.DuckDBPyConnection, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for table in GOLD_TABLES:
        con.execute(f"COPY gold.{table} TO '{(dest / f'{table}.parquet').as_posix()}' (FORMAT parquet)")


def build(cfg: BuildConfig) -> dict[str, int]:
    """Run all stages, block on failed checks, export gold to Parquet. Returns row counts."""
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(cfg.db_path))
    con.execute("SET preserve_insertion_order = false")
    try:
        run_stages(con, cfg)
        failures = run_checks(con)
        if failures:
            raise DataCheckError(failures)
        shutil.rmtree(cfg.out_dir / "gold", ignore_errors=True)
        export_gold(con, cfg.out_dir / "gold")
        return {t: con.execute(f"SELECT count(*) FROM gold.{t}").fetchone()[0] for t in GOLD_TABLES}
    finally:
        con.close()
