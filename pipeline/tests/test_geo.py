import csv

import pytest

from retail_pipeline.geo import daily_weather, locate, write_city_geo, write_weather


def fake_fetch(url):
    if "Nowhere" in url:
        return {}
    return {"results": [
        {"country_code": "CO", "latitude": 1.0, "longitude": 2.0, "population": 999999, "admin1": "Other"},
        {"country_code": "EC", "latitude": -2.17, "longitude": -79.92, "population": 1000, "admin1": "Guayas"},
        {"country_code": "EC", "latitude": -0.22, "longitude": -78.51, "population": 50000, "admin1": "Pichincha"},
    ]}


def test_locate_picks_most_populous_ecuadorian_match():
    assert locate("Quito", fetch=fake_fetch) == ("Quito", -0.22, -78.51, "Pichincha")


def test_locate_fails_without_ecuadorian_match():
    with pytest.raises(ValueError):
        locate("Nowhere", fetch=fake_fetch)


def test_locate_looks_up_alias_but_returns_original_city_name():
    seen_urls = []

    def capturing_fetch(url):
        seen_urls.append(url)
        return fake_fetch(url)

    result = locate("Libertad", fetch=capturing_fetch)
    assert "La+Libertad" in seen_urls[0]
    assert result[0] == "Libertad"


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


def fake_archive(url):
    if "latitude=9.0000" in url:
        raise OSError("HTTP 429")
    return {"daily": {"time": ["2016-01-01", "2016-01-02"], "precipitation_sum": [1.5, None],
                      "temperature_2m_max": [21.0, 22.5]}}


def test_daily_weather_one_row_per_day():
    assert daily_weather(-0.22, -78.51, fetch=fake_archive) == [("2016-01-01", 1.5, 21.0), ("2016-01-02", None, 22.5)]


def _write_geo(csv_dir, rows):
    with open(csv_dir / "city_geo.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["city", "latitude", "longitude", "admin1"])
        writer.writerows(rows)


def test_write_weather_all_cities(tmp_path):
    _write_geo(tmp_path, [("Quito", -0.22, -78.51, "Pichincha"), ("Cuenca", -2.9, -79.0, "Azuay")])
    assert write_weather(tmp_path, fetch=fake_archive, spacing_s=0) == 4
    with open(tmp_path / "weather_daily.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["city", "weather_date", "rain_mm", "temp_max_c"]
    assert rows[1:3] == [["Quito", "2016-01-01", "1.5", "21.0"], ["Quito", "2016-01-02", "", "22.5"]]


def test_failed_weather_call_writes_no_file(tmp_path):
    _write_geo(tmp_path, [("Quito", -0.22, -78.51, "Pichincha"), ("Nowhere", 9.0, 9.0, "")])
    with pytest.raises(OSError):
        write_weather(tmp_path, fetch=fake_archive, spacing_s=0)
    assert not (tmp_path / "weather_daily.csv").exists()


def test_write_weather_retries_a_transient_failure(tmp_path):
    _write_geo(tmp_path, [("Quito", -0.22, -78.51, "Pichincha")])
    calls = []

    def flaky(url):
        calls.append(url)
        if len(calls) == 1:
            raise OSError("connection timed out")
        return fake_archive(url)

    assert write_weather(tmp_path, fetch=flaky, spacing_s=0) == 2
    assert len(calls) == 2
