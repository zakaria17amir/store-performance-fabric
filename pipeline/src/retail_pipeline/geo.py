"""Store-city coordinates and daily weather from the Open-Meteo APIs, loaded into the ERP database."""
import csv
import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import duckdb

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
WEATHER_START, WEATHER_END = "2013-01-01", "2017-08-31"
# the free tier weights a multi-year archive call heavily, so calls are spaced out
CALL_SPACING_S = 15
ATTEMPTS = 3  # per city, for transient network errors

# Names the geocoder doesn't resolve under Favorita's spelling.
LOOKUP_ALIASES = {"Libertad": "La Libertad"}


def _get_json(url: str) -> dict:
    with urlopen(url, timeout=30) as response:
        return json.load(response)


def locate(city: str, fetch=_get_json) -> tuple[str, float, float, str]:
    query = urlencode({
        "name": LOOKUP_ALIASES.get(city, city),
        "count": 10,
        "language": "en",
        "format": "json",
        "countryCode": "EC",
    })
    results = [r for r in fetch(f"{GEOCODING_URL}?{query}").get("results", []) if r.get("country_code") == "EC"]
    if not results:
        raise ValueError(f"No Ecuadorian match for city {city!r}")
    best = max(results, key=lambda r: r.get("population") or 0)
    return city, best["latitude"], best["longitude"], best.get("admin1", "")


def write_city_geo(warehouse: Path, out: Path, fetch=_get_json) -> int:
    con = duckdb.connect(str(warehouse), read_only=True)
    try:
        cities = [r[0] for r in con.execute("SELECT DISTINCT city FROM gold.stg_store ORDER BY city").fetchall()]
    finally:
        con.close()
    rows = [locate(city, fetch) for city in cities]
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "city_geo.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["city", "latitude", "longitude", "admin1"])
        writer.writerows(rows)
    return len(rows)


def daily_weather(latitude: float, longitude: float, fetch=_get_json) -> list[tuple[str, float | None, float | None]]:
    query = urlencode({
        "latitude": f"{latitude:.4f}",
        "longitude": f"{longitude:.4f}",
        "start_date": WEATHER_START,
        "end_date": WEATHER_END,
        "daily": "precipitation_sum,temperature_2m_max",
        "timezone": "America/Guayaquil",
    })
    daily = fetch(f"{ARCHIVE_URL}?{query}")["daily"]
    return list(zip(daily["time"], daily["precipitation_sum"], daily["temperature_2m_max"]))


def write_weather(csv_dir: Path, fetch=_get_json, spacing_s: float = CALL_SPACING_S) -> int:
    """city_geo.csv → weather_daily.csv in the same folder; nothing is written unless every city succeeds."""
    with open(csv_dir / "city_geo.csv", newline="", encoding="utf-8") as f:
        cities = [(r["city"], float(r["latitude"]), float(r["longitude"])) for r in csv.DictReader(f)]
    rows = []
    for i, (city, latitude, longitude) in enumerate(cities):
        if i:
            time.sleep(spacing_s)
        for attempt in range(ATTEMPTS):
            try:
                days = daily_weather(latitude, longitude, fetch)
                break
            except OSError:  # timeouts, connection errors and HTTP errors (429) are all OSError
                if attempt == ATTEMPTS - 1:
                    raise
                time.sleep(4 * spacing_s)
        rows += [(city, *day) for day in days]
    with open(csv_dir / "weather_daily.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["city", "weather_date", "rain_mm", "temp_max_c"])
        writer.writerows(rows)
    return len(rows)
