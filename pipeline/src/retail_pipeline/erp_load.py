"""Create the Azure SQL ERP schema, load the synthetic ERP CSVs, then run the SQL tests."""
import csv
from pathlib import Path

LOAD_ORDER = ("region", "state_region", "store_profile", "item_price",
              "weekday_weight", "sales_target_month", "city_geo", "user_access")


def load_erp(con, csv_dir: Path, sql_dir: Path) -> dict[str, int]:
    cursor = con.cursor()
    cursor.execute((sql_dir / "schema.sql").read_text(encoding="utf-8"))
    cursor.execute((sql_dir / "views.sql").read_text(encoding="utf-8"))
    counts = {}
    for table in LOAD_ORDER:
        with open(csv_dir / f"{table}.csv", newline="", encoding="utf-8") as f:
            header, *rows = list(csv.reader(f))
        cursor.executemany(
            f"INSERT INTO erp.{table} ({', '.join(header)}) VALUES ({', '.join('?' for _ in header)})", rows)
        counts[table] = len(rows)
    cursor.execute((sql_dir / "tests.sql").read_text(encoding="utf-8"))  # THROWs on failure
    con.commit()
    return counts


def connect_azure_sql(server: str, database: str):
    # optional "azure" extra: imported only when needed
    import mssql_python
    from azure.identity import InteractiveBrowserCredential

    # the driver's own ActiveDirectoryInteractive flow fails with "user ''"; a browser token works
    return mssql_python.connect(
        f"Server=tcp:{server},1433;Database={database};Encrypt=yes;",
        token_provider=InteractiveBrowserCredential())
