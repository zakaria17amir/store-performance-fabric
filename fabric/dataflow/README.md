# Dataflow Gen2: df_erp_weather

Paste each `.pq` file into a blank query with the same name (without `.pq`).
Set the three parameters first.

Destinations: output queries (every query not prefixed `fn_` or `src_` — `dim_item`,
`dim_store`, `fact_store_day`, `user_access`, `weather_load_errors`) each get a lakehouse
data destination, table name = query name, replace mode.
Helper queries (`fn_*`, `src_Erp`, `src_Lakehouse`) have no data destination and staging off.
`src_WeatherAttempts` has no data destination but staging **on**: it's referenced by two
queries (`weather_load_errors`, `fact_store_day`), and staging makes the API run once per
refresh instead of twice.

Create the lakehouses with **Lakehouse schemas** unticked — the publish path and
`src_Lakehouse` assume there are no schemas.

Set all three connections (Azure SQL, Lakehouse, Web/Open-Meteo) to privacy level
**Organizational**, and leave "Allow combining data from multiple sources" unticked.

| Parameter | Value |
|---|---|
| `SqlServer` | `<your-server>.database.windows.net` |
| `WorkspaceId` | GUID of the `Retail Data` workspace |
| `LakehouseId` | GUID of the lakehouse |

This dataflow is per-lakehouse: make a copy of `df_erp_weather` for `lh_retail_sample` with
its own `LakehouseId`.

Note: each refresh makes one archive request per store city, 15 seconds apart. Open-Meteo
weights multi-year requests, so a full refresh costs about 120 weighted calls per city (well
within the free daily limit).

Weather data: Open-Meteo.com (CC BY 4.0).
