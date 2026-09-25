"""Store-city coordinates from the Open-Meteo geocoding API (used by the weather dataflow)."""
import csv
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import duckdb

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

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
