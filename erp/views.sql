CREATE OR ALTER VIEW erp.v_sales_target_day AS
WITH days AS (
    SELECT t.store_nbr, t.month_start, t.target_value, DATEADD(day, n.n, t.month_start) AS target_date
    FROM erp.sales_target_month AS t
    CROSS APPLY (
        SELECT TOP (DAY(EOMONTH(t.month_start))) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1 AS n
        FROM sys.all_objects) AS n
),
open_days AS (
    -- planned closures: 25 December and 1 January get no target
    SELECT d.store_nbr, d.month_start, d.target_value, d.target_date, w.weight
    FROM days AS d
    JOIN erp.weekday_weight AS w
        ON w.store_nbr = d.store_nbr
       AND w.weekday_num = DATEDIFF(day, '19000101', d.target_date) % 7 + 1  -- ISO weekday, 1 = Monday
    WHERE NOT (MONTH(d.target_date) = 12 AND DAY(d.target_date) = 25)
      AND NOT (MONTH(d.target_date) = 1 AND DAY(d.target_date) = 1)
),
shares AS (
    SELECT *,
        CAST(ROUND(target_value * weight / SUM(weight) OVER (PARTITION BY store_nbr, month_start), 2)
             AS decimal(14, 2)) AS rounded,
        ROW_NUMBER() OVER (PARTITION BY store_nbr, month_start ORDER BY target_date DESC) AS rn_desc
    FROM open_days
)
SELECT
    store_nbr,
    target_date,
    -- the last open day absorbs rounding so days sum exactly to the month
    rounded + CASE WHEN rn_desc = 1
                   THEN target_value - SUM(rounded) OVER (PARTITION BY store_nbr, month_start)
                   ELSE 0 END AS target_value
FROM shares;
