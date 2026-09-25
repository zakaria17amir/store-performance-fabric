import duckdb
import pytest

from retail_pipeline.__main__ import main
from retail_pipeline.build import GOLD_TABLES, DataCheckError, build
from retail_pipeline.checks import run_checks
from retail_pipeline.config import BuildConfig


def test_build_exports_every_gold_table(full_build):
    cfg, counts = full_build
    assert set(counts) == set(GOLD_TABLES)
    for table in GOLD_TABLES:
        assert (cfg.out_dir / "gold" / f"{table}.parquet").exists()
    assert counts["fact_stockout_risk"] == 2


def test_checks_pass_on_clean_data(warehouse):
    assert run_checks(warehouse) == {}


def test_checks_catch_orphans(raw_dir, tmp_path):
    con = duckdb.connect()
    from retail_pipeline.build import run_stages
    run_stages(con, BuildConfig(raw_dir=raw_dir, out_dir=tmp_path))
    con.execute("INSERT INTO gold.fact_sales VALUES (20160101, 999, 101, 1.0, 0.0, false, false, NULL)")
    assert run_checks(con)["fact_sales_orphan_store"] == 1


def test_failed_checks_block_export(raw_dir, tmp_path, monkeypatch):
    import retail_pipeline.build as b
    monkeypatch.setattr(b, "run_checks", lambda con: {"forced": 1})
    cfg = BuildConfig(raw_dir=raw_dir, out_dir=tmp_path)
    with pytest.raises(DataCheckError):
        b.build(cfg)
    assert not (tmp_path / "gold").exists()


def test_cli_sample_build(raw_dir, tmp_path, capsys):
    main(["build", "--raw", str(raw_dir), "--out", str(tmp_path), "--sample"])
    assert '"stg_store": 4' in capsys.readouterr().out
