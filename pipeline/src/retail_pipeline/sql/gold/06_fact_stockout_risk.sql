CREATE OR REPLACE TABLE gold.fact_stockout_risk AS
WITH pairs AS (
    -- only items that could reach λ ≥ threshold are worth a daily spine
    SELECT store_nbr, item_nbr, min(date) AS first_sale, max(date) AS last_sale
    FROM silver.sales
    WHERE date >= DATE '$stockout_from' - INTERVAL '$lookback_days days' * 2
    GROUP BY store_nbr, item_nbr
    HAVING sum(units) >= $min_expected_units * $lookback_days
),
spine AS (
    SELECT p.store_nbr, p.item_nbr, d.date
    FROM pairs AS p
    JOIN silver.store_day AS d
        ON d.store_nbr = p.store_nbr
       AND d.receipts > 0
       AND d.date BETWEEN p.first_sale AND p.last_sale
),
series AS (
    SELECT sp.store_nbr, sp.item_nbr, sp.date,
           coalesce(s.units, 0) AS units,
           s.store_nbr IS NULL AS no_sale_row
    FROM spine AS sp
    LEFT JOIN silver.sales AS s USING (store_nbr, item_nbr, date)
),
scored AS (
    SELECT
        *,
        avg(units) OVER prev AS lambda_units,
        count(*) OVER prev AS history_days,
        count(*) FILTER (WHERE units > 0) OVER next_days AS future_sales
    FROM series
    WINDOW
        prev AS (PARTITION BY store_nbr, item_nbr ORDER BY date
                 ROWS BETWEEN $lookback_days PRECEDING AND 1 PRECEDING),
        next_days AS (PARTITION BY store_nbr, item_nbr ORDER BY date
                      RANGE BETWEEN INTERVAL '1 day' FOLLOWING AND INTERVAL '$lookback_days days' FOLLOWING)
)
SELECT
    CAST(strftime(date, '%Y%m%d') AS INTEGER) AS date_key,
    store_nbr AS store_key,
    item_nbr AS item_key,
    round(lambda_units, 2) AS expected_units
FROM scored
WHERE date >= DATE '$stockout_from'
  AND no_sale_row
  AND history_days = $lookback_days
  AND lambda_units >= $min_expected_units
  AND future_sales > 0;
