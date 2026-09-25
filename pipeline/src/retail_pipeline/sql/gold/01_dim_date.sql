CREATE OR REPLACE TABLE gold.dim_date AS
WITH bounds AS (
    SELECT min(d) AS lo, max(d) AS hi
    FROM (SELECT date AS d FROM silver.sales UNION ALL SELECT date FROM silver.store_day)
),
days AS (
    SELECT CAST(unnest(generate_series(lo::TIMESTAMP, hi::TIMESTAMP, INTERVAL 1 DAY)) AS DATE) AS date
    FROM bounds
)
SELECT
    CAST(strftime(date, '%Y%m%d') AS INTEGER) AS date_key,
    date,
    year(date) AS year,
    quarter(date) AS quarter,
    month(date) AS month_num,
    strftime(date, '%b') AS month_name,
    year(date) * 100 + month(date) AS month_key,
    weekofyear(date) AS iso_week,
    isoyear(date) AS iso_year,
    isodow(date) AS weekday_num,
    strftime(date, '%a') AS weekday_name,
    isodow(date) >= 6 AS is_weekend,
    date IN (SELECT date FROM silver.national_holidays) AS is_national_holiday
FROM days;
