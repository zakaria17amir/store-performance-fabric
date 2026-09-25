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
JOIN (SELECT store_nbr, min(date) AS opening_date FROM bronze.transactions GROUP BY store_nbr) AS o
    USING (store_nbr)
WHERE s.store_nbr IN (SELECT store_nbr FROM silver.selected_stores);
