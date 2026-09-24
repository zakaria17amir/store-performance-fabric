CREATE OR REPLACE TABLE silver.store_day AS
SELECT date, store_nbr, transactions AS receipts
FROM bronze.transactions
WHERE store_nbr IN (SELECT store_nbr FROM silver.selected_stores)
  AND date >= DATE '$start_date';
