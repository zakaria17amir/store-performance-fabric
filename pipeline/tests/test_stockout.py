def test_only_the_2016_gap_is_flagged(warehouse):
    rows = warehouse.execute(
        "SELECT date_key, store_key, item_key, expected_units FROM gold.fact_stockout_risk ORDER BY 1"
    ).fetchall()
    # 2015-12-15 gap is before the 2016-01-01 cut-off; slow sellers (λ < 3) never flag
    assert rows == [(20160210, 1, 101, 5.0)]


def test_delisting_is_not_flagged(warehouse):
    # store 3 stops selling after 2016-01-31 and never resumes → no flags
    assert warehouse.execute(
        "SELECT count(*) FROM gold.fact_stockout_risk WHERE store_key = 3").fetchone()[0] == 0
