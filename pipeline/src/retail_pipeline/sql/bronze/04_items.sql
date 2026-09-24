CREATE OR REPLACE TABLE bronze.items AS
SELECT *
FROM read_csv('$raw_dir/items.csv', header = true, columns = {
    'item_nbr': 'INTEGER', 'family': 'VARCHAR', 'class': 'INTEGER', 'perishable': 'INTEGER'});
