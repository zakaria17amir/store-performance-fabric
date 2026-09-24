"""Seeded synthetic ERP data. Favorita has units only; these tables supply prices,
costs, regions, store profiles and targets. Every column here is synthetic except
the keys it inherits from the gold tables."""
import csv
import random
from datetime import date
from pathlib import Path

import duckdb

REGIONS = ("Quito", "Guayaquil", "Sierra", "Costa & Oriente")
STATE_REGION = {
    "Pichincha": "Quito",
    "Guayas": "Guayaquil",
    "Azuay": "Sierra", "Bolivar": "Sierra", "Chimborazo": "Sierra", "Cotopaxi": "Sierra",
    "Imbabura": "Sierra", "Loja": "Sierra", "Tungurahua": "Sierra",
    "El Oro": "Costa & Oriente", "Esmeraldas": "Costa & Oriente", "Los Rios": "Costa & Oriente",
    "Manabi": "Costa & Oriente", "Santa Elena": "Costa & Oriente",
    "Santo Domingo de los Tsachilas": "Costa & Oriente", "Pastaza": "Costa & Oriente",
}
STORE_AREA_M2 = {"A": (2500, 4000), "B": (1800, 3000), "C": (1200, 2200), "D": (900, 1600), "E": (600, 1200)}
# family → (min price USD, max price USD, gross margin rate)
FAMILY_PRICING = {
    "AUTOMOTIVE": (2.0, 30.0, 0.35), "BABY CARE": (2.0, 15.0, 0.30), "BEAUTY": (2.0, 15.0, 0.45),
    "BEVERAGES": (0.4, 4.0, 0.25), "BOOKS": (3.0, 25.0, 0.30), "BREAD/BAKERY": (0.3, 3.5, 0.35),
    "CELEBRATION": (1.0, 12.0, 0.40), "CLEANING": (1.0, 8.0, 0.28), "DAIRY": (0.6, 5.0, 0.20),
    "DELI": (1.5, 10.0, 0.30), "EGGS": (1.5, 4.5, 0.15), "FROZEN FOODS": (1.5, 9.0, 0.25),
    "GROCERY I": (0.5, 6.0, 0.22), "GROCERY II": (0.5, 7.0, 0.24), "HARDWARE": (2.0, 30.0, 0.35),
    "HOME AND KITCHEN I": (2.0, 25.0, 0.40), "HOME AND KITCHEN II": (2.0, 25.0, 0.40),
    "HOME APPLIANCES": (15.0, 150.0, 0.18), "HOME CARE": (1.0, 8.0, 0.30), "LADIESWEAR": (5.0, 40.0, 0.50),
    "LAWN AND GARDEN": (2.0, 20.0, 0.35), "LINGERIE": (3.0, 20.0, 0.50), "LIQUOR,WINE,BEER": (1.0, 20.0, 0.30),
    "MAGAZINES": (1.0, 6.0, 0.20), "MEATS": (3.0, 12.0, 0.20), "PERSONAL CARE": (1.0, 9.0, 0.35),
    "PET SUPPLIES": (1.0, 15.0, 0.30), "PLAYERS AND ELECTRONICS": (10.0, 120.0, 0.18),
    "POULTRY": (2.0, 8.0, 0.18), "PREPARED FOODS": (2.0, 9.0, 0.40), "PRODUCE": (0.3, 3.0, 0.30),
    "SCHOOL AND OFFICE SUPPLIES": (0.5, 10.0, 0.40), "SEAFOOD": (3.0, 15.0, 0.25),
}
FULL_MONTH_MIN_DAYS = 25
GROWTH_MEAN, GROWTH_SD = 0.03, 0.02

SALES_VALUE_BY_STORE_MONTH = """
SELECT f.store_key, CAST(date_trunc('month', d.date) AS DATE) AS month_start,
       sum(f.units * p.unit_price) AS sales_value, count(DISTINCT d.date) AS active_days
FROM gold.fact_sales AS f
JOIN gold.dim_date AS d USING (date_key)
JOIN erp_item_price AS p USING (item_key)
GROUP BY ALL
ORDER BY 1, 2
"""
WEEKDAY_WEIGHTS = """
SELECT f.store_key, d.weekday_num,
       sum(f.units * p.unit_price) / sum(sum(f.units * p.unit_price)) OVER (PARTITION BY f.store_key) AS weight
FROM gold.fact_sales AS f
JOIN gold.dim_date AS d USING (date_key)
JOIN erp_item_price AS p USING (item_key)
GROUP BY f.store_key, d.weekday_num
ORDER BY 1, 2
"""


def region_for(state: str) -> str:
    try:
        return STATE_REGION[state]
    except KeyError:
        raise ValueError(f"No region mapping for state {state!r}") from None


def generate_erp(con: duckdb.DuckDBPyConnection, seed: int = 42) -> dict[str, list[tuple]]:
    rng = random.Random(seed)
    stores = con.execute("SELECT store_nbr, state, store_type FROM gold.stg_store ORDER BY store_nbr").fetchall()
    items = con.execute("SELECT item_key, family FROM gold.stg_item ORDER BY item_key").fetchall()

    region = [(i + 1, name) for i, name in enumerate(REGIONS)]
    region_id = {name: rid for rid, name in region}
    state_region = sorted({(state, region_id[region_for(state)]) for _, state, _ in stores})
    store_profile = [(nbr, rng.randint(*STORE_AREA_M2[store_type])) for nbr, _, store_type in stores]

    item_price = []
    for item, family in items:
        if family not in FAMILY_PRICING:
            raise ValueError(f"No pricing for family {family!r}")
        low, high, margin = FAMILY_PRICING[family]
        price = round(rng.uniform(low, high), 2)
        item_price.append((item, price, round(price * (1 - margin), 2)))

    con.execute("CREATE OR REPLACE TEMP TABLE erp_item_price (item_key INTEGER, unit_price DOUBLE, unit_cost DOUBLE)")
    con.executemany("INSERT INTO erp_item_price VALUES (?, ?, ?)", item_price)
    weekday_weight = [(s, w, float(v)) for s, w, v in con.execute(WEEKDAY_WEIGHTS).fetchall()]
    monthly = con.execute(SALES_VALUE_BY_STORE_MONTH).fetchall()

    full_months = {(s, m): v for s, m, v, days in monthly if days >= FULL_MONTH_MIN_DAYS}
    targets = []
    for store, month, _, _ in monthly:
        prior = full_months.get((store, month.replace(year=month.year - 1)))
        if prior is not None:
            growth = rng.gauss(GROWTH_MEAN, GROWTH_SD)
            targets.append((store, month, round(prior * (1 + growth), 2)))

    return {
        "region": region,
        "state_region": state_region,
        "store_profile": store_profile,
        "item_price": item_price,
        "weekday_weight": weekday_weight,
        "sales_target_month": targets,
    }


COLUMNS = {
    "region": ("region_id", "region_name"),
    "state_region": ("state", "region_id"),
    "store_profile": ("store_nbr", "selling_area_m2"),
    "item_price": ("item_nbr", "unit_price", "unit_cost"),
    "weekday_weight": ("store_nbr", "weekday_num", "weight"),
    "sales_target_month": ("store_nbr", "month_start", "target_value"),
}


def write_erp_seed(warehouse: Path, out: Path, seed: int = 42) -> dict[str, int]:
    out.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(warehouse), read_only=True)
    try:
        tables = generate_erp(con, seed)
    finally:
        con.close()
    for name, rows in tables.items():
        with open(out / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS[name])
            writer.writerows(rows)
    return {name: len(rows) for name, rows in tables.items()}
