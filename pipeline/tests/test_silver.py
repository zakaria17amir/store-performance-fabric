from datetime import date


def test_full_build_keeps_all_stores(warehouse):
    stores = [r[0] for r in warehouse.execute(
        "SELECT store_nbr FROM silver.selected_stores ORDER BY 1").fetchall()]
    assert stores == [1, 2, 3, 4, 5]


def test_sample_keeps_top_quito_and_guayaquil(sample_warehouse):
    stores = [r[0] for r in sample_warehouse.execute(
        "SELECT store_nbr FROM silver.selected_stores ORDER BY 1").fetchall()]
    assert stores == [1, 2, 3, 4]  # Cuenca (store 5) excluded; ≤3 per city


def test_sample_starts_2016(sample_warehouse):
    assert sample_warehouse.execute("SELECT min(date) FROM silver.sales").fetchone()[0] == date(2016, 1, 1)


def test_returns_are_split_from_units(warehouse):
    row = warehouse.execute(
        "SELECT units, return_units FROM silver.sales "
        "WHERE store_nbr = 2 AND item_nbr = 101 AND date = DATE '2016-01-05'").fetchone()
    assert row == (0.0, 1.0)


def test_store_day_receipts(warehouse):
    assert warehouse.execute(
        "SELECT receipts FROM silver.store_day WHERE store_nbr = 1 AND date = DATE '2016-02-10'"
    ).fetchone()[0] == 100


def test_national_holidays_respect_transfers(warehouse):
    days = {r[0] for r in warehouse.execute("SELECT date FROM silver.national_holidays").fetchall()}
    assert days == {date(2016, 1, 1), date(2016, 2, 9)}  # 02-08 transferred, 03-05 local
