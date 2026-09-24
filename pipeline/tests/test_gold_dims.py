from datetime import date


def test_dim_date_covers_sales_and_receipts(warehouse):
    lo, hi, n = warehouse.execute("SELECT min(date), max(date), count(*) FROM gold.dim_date").fetchone()
    assert (lo, hi) == (date(2015, 1, 1), date(2016, 3, 31))
    assert n == (hi - lo).days + 1


def test_dim_date_attributes(warehouse):
    row = warehouse.execute(
        "SELECT date_key, month_key, weekday_num, weekday_name, is_weekend, is_national_holiday "
        "FROM gold.dim_date WHERE date = DATE '2016-01-02'").fetchone()
    assert row == (20160102, 201601, 6, "Sat", True, False)


def test_dim_date_holidays(warehouse):
    flags = dict(warehouse.execute(
        "SELECT date, is_national_holiday FROM gold.dim_date "
        "WHERE date IN (DATE '2016-01-01', DATE '2016-02-08', DATE '2016-02-09')").fetchall())
    assert flags == {date(2016, 1, 1): True, date(2016, 2, 8): False, date(2016, 2, 9): True}
    assert warehouse.execute(
        "SELECT iso_year, iso_week FROM gold.dim_date WHERE date = DATE '2016-01-01'"
    ).fetchone() == (2015, 53)


def test_opening_date_uses_full_receipt_history(sample_warehouse):
    # the sample starts 2016-01-01, but store 2 has traded since 2015-06-01
    assert sample_warehouse.execute(
        "SELECT opening_date FROM gold.stg_store WHERE store_key = 2").fetchone()[0] == date(2015, 6, 1)


def test_opening_date_null_when_trading_since_data_start(sample_warehouse):
    # store 1's first receipt (2015-01-01) IS the fixture's first transactions date, so it
    # was already trading when the data starts: opening_date is unknown, not left-censored.
    assert sample_warehouse.execute(
        "SELECT opening_date FROM gold.stg_store WHERE store_key = 1").fetchone()[0] is None


def test_stg_item_perishable_flag(warehouse):
    assert warehouse.execute(
        "SELECT family, is_perishable FROM gold.stg_item WHERE item_key = 102").fetchone() == ("PRODUCE", True)


def test_stg_store_day_keys(warehouse):
    assert warehouse.execute(
        "SELECT receipts FROM gold.stg_store_day WHERE store_key = 3 AND date_key = 20160115"
    ).fetchone()[0] == 90
