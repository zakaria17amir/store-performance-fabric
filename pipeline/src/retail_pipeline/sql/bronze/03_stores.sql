CREATE OR REPLACE TABLE bronze.stores AS
SELECT *
FROM read_csv('$raw_dir/stores.csv', header = true, columns = {
    'store_nbr': 'INTEGER', 'city': 'VARCHAR', 'state': 'VARCHAR', 'type': 'VARCHAR', 'cluster': 'INTEGER'});
