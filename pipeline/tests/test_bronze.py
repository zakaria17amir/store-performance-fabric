import duckdb
import pytest

from fixture_data import write_fixture
from retail_pipeline.build import run_stages
from retail_pipeline.config import BuildConfig


def test_bronze_tables_are_typed(warehouse):
    cols = dict(warehouse.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_schema = 'bronze' AND table_name = 'train'").fetchall())
    assert cols == {"id": "BIGINT", "date": "DATE", "store_nbr": "INTEGER",
                    "item_nbr": "INTEGER", "unit_sales": "DOUBLE", "onpromotion": "BOOLEAN"}


def test_empty_promotion_flag_is_null(warehouse):
    nulls = warehouse.execute(
        "SELECT count(*) FROM bronze.train WHERE store_nbr = 2 AND onpromotion IS NULL").fetchone()[0]
    assert nulls == 91  # store 2: 2016-01-01..2016-03-31, promo flag empty


def test_schema_drift_fails(tmp_path):
    raw = write_fixture(tmp_path / "raw", extra_store_column=True)
    with pytest.raises(duckdb.Error):
        run_stages(duckdb.connect(), BuildConfig(raw_dir=raw, out_dir=tmp_path / "out"), ("bronze",))
