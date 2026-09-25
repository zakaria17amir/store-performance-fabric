CREATE OR REPLACE TABLE bronze.holidays_events AS
SELECT *
FROM read_csv('$raw_dir/holidays_events.csv', header = true, columns = {
    'date': 'DATE', 'type': 'VARCHAR', 'locale': 'VARCHAR', 'locale_name': 'VARCHAR',
    'description': 'VARCHAR', 'transferred': 'BOOLEAN'});
