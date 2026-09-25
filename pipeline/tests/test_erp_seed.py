from datetime import date

import pytest

from retail_pipeline.erp_seed import generate_erp, region_for


@pytest.fixture(scope="module")
def erp(warehouse):
    return generate_erp(warehouse, seed=42)


def test_is_deterministic(warehouse, erp):
    assert generate_erp(warehouse, seed=42) == erp


def test_region_mapping():
    assert region_for("Pichincha") == "Quito"
    assert region_for("Azuay") == "Sierra"
    with pytest.raises(ValueError):
        region_for("Atlantis")


def test_cost_below_price(erp):
    assert all(0 < cost < price for _, price, cost in erp["item_price"])


def test_weekday_weights_sum_to_one(erp):
    totals = {}
    for store, _, weight in erp["weekday_weight"]:
        totals[store] = totals.get(store, 0) + weight
    assert totals and all(t == pytest.approx(1.0) for t in totals.values())


def test_targets_need_a_full_prior_year_month(erp):
    months = {(s, m) for s, m, _ in erp["sales_target_month"]}
    assert (1, date(2016, 1, 1)) in months      # 2015-01 is a full month for store 1
    assert not any(m.year == 2015 for _, m in months)
    assert not any(s == 3 for s, _ in months)  # store 3 has no prior year


def test_target_growth_is_plausible(warehouse, erp):
    price = {item: p for item, p, _ in erp["item_price"]}
    prior = sum(units * price[item] for item, units in warehouse.execute(
        "SELECT item_key, sum(units) FROM gold.fact_sales "
        "WHERE store_key = 1 AND date_key BETWEEN 20150101 AND 20150131 GROUP BY 1").fetchall())
    target = next(v for s, m, v in erp["sales_target_month"] if s == 1 and m == date(2016, 1, 1))
    assert -0.10 < target / prior - 1 < 0.16
