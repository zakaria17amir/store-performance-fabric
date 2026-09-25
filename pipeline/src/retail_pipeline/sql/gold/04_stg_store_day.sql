CREATE OR REPLACE TABLE gold.stg_store_day AS
SELECT CAST(strftime(date, '%Y%m%d') AS INTEGER) AS date_key, store_nbr AS store_key, receipts
FROM silver.store_day;
