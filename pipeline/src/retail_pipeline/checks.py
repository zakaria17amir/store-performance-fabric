"""Data checks. Each query returns the number of violating rows (0 = pass)."""
import duckdb


def _orphans(fact: str, key: str, dim: str) -> str:
    return f"SELECT count(*) FROM gold.{fact} ANTI JOIN gold.{dim} USING ({key})"


CHECKS: dict[str, str] = {
    "dim_date_unique_key": "SELECT count(*) - count(DISTINCT date_key) FROM gold.dim_date",
    "stg_store_unique_key": "SELECT count(*) - count(DISTINCT store_key) FROM gold.stg_store",
    "stg_item_unique_key": "SELECT count(*) - count(DISTINCT item_key) FROM gold.stg_item",
    "fact_sales_unique_grain": (
        "SELECT count(*) FROM (SELECT 1 FROM gold.fact_sales "
        "GROUP BY date_key, store_key, item_key HAVING count(*) > 1)"),
    "fact_sales_orphan_date": _orphans("fact_sales", "date_key", "dim_date"),
    "fact_sales_orphan_store": _orphans("fact_sales", "store_key", "stg_store"),
    "fact_sales_orphan_item": _orphans("fact_sales", "item_key", "stg_item"),
    "stockout_orphan_date": _orphans("fact_stockout_risk", "date_key", "dim_date"),
    "stockout_orphan_store": _orphans("fact_stockout_risk", "store_key", "stg_store"),
    "stockout_orphan_item": _orphans("fact_stockout_risk", "item_key", "stg_item"),
    "store_day_orphan_date": _orphans("stg_store_day", "date_key", "dim_date"),
    "store_day_orphan_store": _orphans("stg_store_day", "store_key", "stg_store"),
    "stg_store_day_unique_grain": "SELECT count(*) - count(DISTINCT (date_key, store_key)) FROM gold.stg_store_day",
    "stockout_unique_grain": "SELECT count(*) - count(DISTINCT (date_key, store_key, item_key)) FROM gold.fact_stockout_risk",
    "store_days_without_sales": (
        "SELECT count(*) FROM silver.store_day d WHERE receipts > 0 AND NOT EXISTS "
        "(SELECT 1 FROM silver.sales s WHERE s.store_nbr = d.store_nbr AND s.date = d.date)"),
    "negative_units": "SELECT count(*) FROM gold.fact_sales WHERE units < 0 OR return_units < 0",
    "store_type_values": "SELECT count(*) FROM gold.stg_store WHERE store_type NOT IN ('A','B','C','D','E')",
    "totals_reconcile_by_year": """
        WITH g AS (SELECT date_key // 10000 AS yr, sum(units - return_units) AS v
                   FROM gold.fact_sales GROUP BY 1),
             b AS (SELECT year(date) AS yr, sum(unit_sales) AS v FROM bronze.train
                   WHERE store_nbr IN (SELECT store_nbr FROM silver.selected_stores) GROUP BY 1)
        SELECT count(*) FROM g FULL JOIN b USING (yr)
        WHERE abs(coalesce(g.v, 0) - coalesce(b.v, 0)) > 1e-6 * greatest(abs(coalesce(b.v, 0)), 1)
    """,
}


def run_checks(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    failures = {}
    for name, sql in CHECKS.items():
        violations = con.execute(sql).fetchone()[0]
        if violations:
            failures[name] = violations
    return failures
