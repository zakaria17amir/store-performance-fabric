CREATE OR REPLACE TABLE silver.selected_stores AS
WITH volume AS (
    SELECT s.store_nbr, s.city, coalesce(sum(t.transactions), 0) AS receipts
    FROM bronze.stores AS s
    LEFT JOIN bronze.transactions AS t
        ON t.store_nbr = s.store_nbr AND t.date >= DATE '2016-01-01'
    GROUP BY s.store_nbr, s.city
),
ranked AS (
    SELECT store_nbr, city,
           row_number() OVER (PARTITION BY city ORDER BY receipts DESC, store_nbr) AS rank_in_city
    FROM volume
)
SELECT store_nbr
FROM ranked
WHERE NOT $sample OR (city IN ('Quito', 'Guayaquil') AND rank_in_city <= 3);
