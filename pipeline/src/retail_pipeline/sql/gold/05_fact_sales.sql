CREATE OR REPLACE TABLE gold.fact_sales AS
WITH windowed AS (
    SELECT
        date, store_nbr, item_nbr, units, return_units, on_promo,
        min(date) OVER (PARTITION BY store_nbr, item_nbr) AS first_sale,
        sum(CASE WHEN on_promo IS TRUE THEN 0 ELSE units END) OVER lookback AS base_units_sum,
        count(*) FILTER (WHERE on_promo) OVER lookback AS promo_days_in_lookback,
        count(*) FILTER (WHERE on_promo) OVER recent AS promo_days_recent
    FROM silver.sales
    WINDOW
        lookback AS (PARTITION BY store_nbr, item_nbr ORDER BY date
                     RANGE BETWEEN INTERVAL '$lookback_days days' PRECEDING
                               AND INTERVAL '1 day' PRECEDING),
        recent AS (PARTITION BY store_nbr, item_nbr ORDER BY date
                   RANGE BETWEEN INTERVAL '$post_promo_days days' PRECEDING
                             AND INTERVAL '1 day' PRECEDING)
),
flagged AS (
    SELECT
        *,
        on_promo IS NOT TRUE AND promo_days_recent > 0 AS post_promo_window,
        datediff('day', first_sale, date) >= $lookback_days AS has_full_history
    FROM windowed
)
SELECT
    CAST(strftime(date, '%Y%m%d') AS INTEGER) AS date_key,
    store_nbr AS store_key,
    item_nbr AS item_key,
    units,
    return_units,
    on_promo,
    post_promo_window,
    CASE
        WHEN (on_promo IS TRUE OR post_promo_window) AND has_full_history
        -- days without a sales row count as zero units; promo days are excluded
        THEN coalesce(base_units_sum, 0) / nullif($lookback_days - promo_days_in_lookback, 0)
    END AS baseline_units
FROM flagged;
