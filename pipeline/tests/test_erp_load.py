import csv

from retail_pipeline.erp_load import LOAD_ORDER, load_erp


class FakeCursor:
    def __init__(self, log):
        self.log = log

    def execute(self, sql):
        self.log.append(("execute", sql.split()[0]))

    def executemany(self, sql, rows):
        self.rows = list(rows)
        self.log.append(("executemany", sql, len(self.rows)))


class FakeConnection:
    def __init__(self):
        self.log = []

    def cursor(self):
        return FakeCursor(self.log)

    def commit(self):
        self.log.append(("commit",))


def test_load_order_runs_schema_views_inserts_tests_then_commits(tmp_path):
    sql = tmp_path / "sql"
    sql.mkdir()
    for name, first_word in (("schema", "DROP"), ("views", "CREATE"), ("tests", "IF")):
        (sql / f"{name}.sql").write_text(f"{first_word} ...", encoding="utf-8")
    data = tmp_path / "csv"
    data.mkdir()
    for table in LOAD_ORDER:
        with open(data / f"{table}.csv", "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows([["a", "b"], ["1", "2"], ["3", "4"]])
    con = FakeConnection()

    counts = load_erp(con, data, sql)

    assert counts == {table: 2 for table in LOAD_ORDER}
    assert con.log[0] == ("execute", "DROP") and con.log[1] == ("execute", "CREATE")
    inserts = [entry for entry in con.log if entry[0] == "executemany"]
    assert [e[1] for e in inserts] == [f"INSERT INTO erp.{t} (a, b) VALUES (?, ?)" for t in LOAD_ORDER]
    assert con.log[-2:] == [("execute", "IF"), ("commit",)]


def test_empty_csv_cells_load_as_null(tmp_path):
    sql = tmp_path / "sql"
    sql.mkdir()
    for name in ("schema", "views", "tests"):
        (sql / f"{name}.sql").write_text("SELECT 1", encoding="utf-8")
    data = tmp_path / "csv"
    data.mkdir()
    for table in LOAD_ORDER:
        with open(data / f"{table}.csv", "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows([["city", "rain_mm"], ["Quito", ""]])
    cursors = []
    con = FakeConnection()
    con.cursor = lambda: cursors.append(FakeCursor(con.log)) or cursors[-1]

    load_erp(con, data, sql)

    assert cursors[0].rows == [["Quito", None]]
