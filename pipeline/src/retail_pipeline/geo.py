"""Store-city coordinates from the Open-Meteo geocoding API (used by the weather dataflow)."""
import csv
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import duckdb

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def _get_json(url: str) -> dict:
    with urlopen(url, timeout=30) as response:
        return json.load(response)


def locate(city: str, fetch=_get_json) -> tuple[str, float, float, str]:
    query = urlencode({"name": city, "count": 10, "language": "en", "format": "json"})
    for result in fetch(f"{GEOCODING_URL}?{query}").get("results", []):
        if result.get("country_code") == "EC":
            return city, result["latitude"], result["longitude"], result.get("admin1", "")
    raise ValueError(f"No Ecuadorian match for city {city!r}")


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
