CREATE OR REPLACE TABLE bronze.train AS
SELECT *
FROM read_csv('$raw_dir/train.csv', header = true, columns = {
    'id': 'BIGINT', 'date': 'DATE', 'store_nbr': 'INTEGER', 'item_nbr': 'INTEGER',
    'unit_sales': 'DOUBLE', 'onpromotion': 'BOOLEAN'})
WHERE date >= DATE '$start_date';
