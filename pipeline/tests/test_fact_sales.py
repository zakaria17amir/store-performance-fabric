import pytest


def row(con, date_key, store=1, item=102):
    return con.execute(
        "SELECT on_promo, post_promo_window, baseline_units FROM gold.fact_sales "
        "WHERE date_key = ? AND store_key = ? AND item_key = ?", [date_key, store, item]).fetchone()


def test_baseline_on_first_promo_day(warehouse):
    # 27 trading days before 2016-01-10 (28 calendar days minus the 12-25 closure);
    # 26 rows sell (12-20 is a genuine zero-sale trading day) × 2 units → 52 / 27
    on_promo, post, baseline = row(warehouse, 20160110)
    assert on_promo is True and post is False
    assert baseline == pytest.approx(52 / 27)


def test_baseline_excludes_promo_days(warehouse):
    # 2016-01-11: 27 trading days − 1 promo day; 25 non-promo rows × 2 → 50 / 26
    assert row(warehouse, 20160111)[2] == pytest.approx(50 / 26)


def test_post_promo_window(warehouse):
    on_promo, post, baseline = row(warehouse, 20160113)
    assert (on_promo, post) == (False, True)
    # 27 trading days − 3 promo days; 23 non-promo rows × 2 → 46 / 24
    assert baseline == pytest.approx(46 / 24)


def test_no_baseline_outside_promo_windows(warehouse):
    assert row(warehouse, 20160120) == (False, False, None)


def test_no_baseline_without_history(warehouse):
    # store 3 only sells from 2016-01-01: never enough history → always null
    assert warehouse.execute(
        "SELECT count(*) FROM gold.fact_sales WHERE store_key = 3 AND baseline_units IS NOT NULL"
    ).fetchone()[0] == 0


def test_unknown_promo_flag_stays_null(warehouse):
    assert warehouse.execute(
        "SELECT count(*) FROM gold.fact_sales WHERE store_key = 2 AND on_promo IS NULL"
    ).fetchone()[0] == 91
