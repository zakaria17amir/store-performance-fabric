CREATE OR REPLACE TABLE silver.national_holidays AS
SELECT DISTINCT date
FROM bronze.holidays_events
WHERE locale = 'National'
  AND type IN ('Holiday', 'Transfer', 'Additional', 'Bridge')
  AND NOT transferred;
