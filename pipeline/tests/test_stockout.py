def test_only_2016_gaps_are_flagged(warehouse):
    rows = warehouse.execute(
        "SELECT date_key, store_key, item_key, expected_units FROM gold.fact_stockout_risk ORDER BY 1"
    ).fetchall()
    # 2015-12-15 gap is before the 2016-01-01 cut-off; slow sellers (λ < 3) never flag.
    # λ on 2016-01-01 = previous 28 trading days 2015-12-03..2015-12-31 minus the 12-25
    # closure; includes the 2015-12-15 zero day → 27 × 5 / 28 = 4.82
    # 2016-03-01 is a partial trading day (20 receipts vs. 100) → not flagged
    assert rows == [(20160101, 1, 101, 4.82), (20160210, 1, 101, 5.0)]


def test_delisting_is_not_flagged(warehouse):
    # store 3 stops selling after 2016-01-31 and never resumes → no flags
    assert warehouse.execute(
        "SELECT count(*) FROM gold.fact_stockout_risk WHERE store_key = 3").fetchone()[0] == 0
