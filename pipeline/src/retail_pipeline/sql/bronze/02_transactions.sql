CREATE OR REPLACE TABLE bronze.transactions AS
SELECT *
FROM read_csv('$raw_dir/transactions.csv', header = true, columns = {
    'date': 'DATE', 'store_nbr': 'INTEGER', 'transactions': 'INTEGER'});
