import csv

import pytest

from retail_pipeline.geo import locate, write_city_geo


def fake_fetch(url):
    if "Nowhere" in url:
        return {}
    return {"results": [
        {"country_code": "CO", "latitude": 1.0, "longitude": 2.0, "admin1": "Other"},
        {"country_code": "EC", "latitude": -0.22, "longitude": -78.51, "admin1": "Pichincha"},
    ]}


def test_locate_picks_first_ecuadorian_match():
    assert locate("Quito", fetch=fake_fetch) == ("Quito", -0.22, -78.51, "Pichincha")


def test_locate_fails_without_ecuadorian_match():
    with pytest.raises(ValueError):
        locate("Nowhere", fetch=fake_fetch)


def test_write_city_geo_one_row_per_store_city(full_build, tmp_path):
    cfg, _ = full_build
    assert write_city_geo(cfg.db_path, tmp_path, fetch=fake_fetch) == 3  # Quito, Guayaquil, Cuenca
    with open(tmp_path / "city_geo.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["city", "latitude", "longitude", "admin1"]
    assert sorted(r[0] for r in rows[1:]) == ["Cuenca", "Guayaquil", "Quito"]


def test_failed_lookup_writes_no_file(full_build, tmp_path):
    cfg, _ = full_build

    def fetch_fails_for_quito(url):
        return {} if "Quito" in url else fake_fetch(url)

    with pytest.raises(ValueError):
        write_city_geo(cfg.db_path, tmp_path, fetch=fetch_fails_for_quito)
    assert not (tmp_path / "city_geo.csv").exists()
