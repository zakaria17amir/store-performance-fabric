IF EXISTS (
    SELECT 1
    FROM erp.sales_target_month AS m
    JOIN (SELECT store_nbr, DATEFROMPARTS(YEAR(target_date), MONTH(target_date), 1) AS month_start,
                 SUM(target_value) AS total
          FROM erp.v_sales_target_day
          GROUP BY store_nbr, DATEFROMPARTS(YEAR(target_date), MONTH(target_date), 1)) AS d
        ON d.store_nbr = m.store_nbr AND d.month_start = m.month_start
    WHERE d.total <> m.target_value)
    THROW 50001, 'Daily targets do not sum to the monthly target', 1;
IF EXISTS (SELECT 1 FROM erp.v_sales_target_day
           WHERE (MONTH(target_date) = 12 AND DAY(target_date) = 25) OR (MONTH(target_date) = 1 AND DAY(target_date) = 1))
    THROW 50002, 'A target was allocated to a planned closure day', 1;
IF EXISTS (SELECT 1 FROM erp.sales_target_month AS m
           WHERE NOT EXISTS (SELECT 1 FROM erp.v_sales_target_day AS d
                             WHERE d.store_nbr = m.store_nbr AND d.target_date BETWEEN m.month_start AND EOMONTH(m.month_start)))
    THROW 50003, 'A monthly target has no daily allocation', 1;
IF EXISTS (SELECT 1 FROM erp.city_geo AS g
           WHERE NOT EXISTS (SELECT 1 FROM erp.weather_daily AS w WHERE w.city = g.city))
    THROW 50004, 'A store city has no weather', 1;
