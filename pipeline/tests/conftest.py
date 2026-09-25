import duckdb
import pytest

from fixture_data import write_fixture
from retail_pipeline.build import build, run_stages
from retail_pipeline.config import BuildConfig, sample_config


@pytest.fixture(scope="session")
def raw_dir(tmp_path_factory):
    return write_fixture(tmp_path_factory.mktemp("raw"))


@pytest.fixture(scope="session")
def warehouse(raw_dir, tmp_path_factory):
    con = duckdb.connect()
    run_stages(con, BuildConfig(raw_dir=raw_dir, out_dir=tmp_path_factory.mktemp("unused")))
    yield con
    con.close()


@pytest.fixture(scope="session")
def sample_warehouse(raw_dir, tmp_path_factory):
    con = duckdb.connect()
    run_stages(con, sample_config(raw_dir, tmp_path_factory.mktemp("unused_sample")))
    yield con
    con.close()


@pytest.fixture(scope="session")
def full_build(raw_dir, tmp_path_factory):
    cfg = BuildConfig(raw_dir=raw_dir, out_dir=tmp_path_factory.mktemp("full"))
    return cfg, build(cfg)
