CREATE OR REPLACE TABLE gold.stg_store AS
SELECT
    s.store_nbr AS store_key,
    s.store_nbr,
    s.city,
    s.state,
    s.type AS store_type,
    s.cluster,
    o.opening_date
FROM bronze.stores AS s
JOIN (
    -- a store whose first receipt falls within 7 days of the data's first date was already
    -- trading when the data starts, so its true opening date is unknown, not that first receipt.
    SELECT store_nbr,
        CASE WHEN min(date) <= (SELECT min(date) FROM bronze.transactions) + INTERVAL 7 DAY
            THEN NULL ELSE min(date) END AS opening_date
    FROM bronze.transactions
    GROUP BY store_nbr
) AS o
    USING (store_nbr)
WHERE s.store_nbr IN (SELECT store_nbr FROM silver.selected_stores);
