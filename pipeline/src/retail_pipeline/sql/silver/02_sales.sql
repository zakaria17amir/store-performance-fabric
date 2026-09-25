CREATE OR REPLACE TABLE silver.sales AS
SELECT
    date,
    store_nbr,
    item_nbr,
    sum(greatest(unit_sales, 0)) AS units,
    sum(greatest(-unit_sales, 0)) AS return_units,
    bool_or(onpromotion) AS on_promo
FROM bronze.train
WHERE store_nbr IN (SELECT store_nbr FROM silver.selected_stores)
GROUP BY date, store_nbr, item_nbr;
