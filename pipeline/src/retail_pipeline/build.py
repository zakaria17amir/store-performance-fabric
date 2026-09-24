from pathlib import Path
from string import Template

import duckdb

from .config import BuildConfig

SQL_DIR = Path(__file__).parent / "sql"
STAGES = ("bronze", "silver", "gold")


def sql_params(cfg: BuildConfig) -> dict[str, str]:
    return {
        "raw_dir": cfg.raw_dir.resolve().as_posix(),
        "sample": "true" if cfg.sample else "false",
        "start_date": cfg.start_date.isoformat(),
        "stockout_from": cfg.stockout_from.isoformat(),
        "lookback_days": str(cfg.lookback_days),
        "min_expected_units": str(cfg.min_expected_units),
        "post_promo_days": str(cfg.post_promo_days),
    }


def run_stages(con: duckdb.DuckDBPyConnection, cfg: BuildConfig, stages=STAGES) -> None:
    """Run every SQL file of each stage in file-name order. One statement per file."""
    params = sql_params(cfg)
    for stage in stages:
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {stage}")
        for path in sorted((SQL_DIR / stage).glob("*.sql")):
            con.execute(Template(path.read_text(encoding="utf-8")).substitute(params))
