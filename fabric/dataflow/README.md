# Dataflow Gen2: df_erp_weather

Paste each `.pq` file into a blank query with the same name (without `.pq`).
Set the three parameters first.

Destinations: the four output queries (`dim_item`, `dim_store`, `fact_store_day`,
`user_access`) each get a lakehouse data destination, table name = query name, replace mode.
The helper queries (`src_Erp`, `src_Lakehouse`) have no data destination and staging off.

Create the lakehouses with **Lakehouse schemas** unticked — the publish path and
`src_Lakehouse` assume there are no schemas.

Set both connections (Azure SQL, Lakehouse) to privacy level
**Organizational**, and leave "Allow combining data from multiple sources" unticked.

| Parameter | Value |
|---|---|
| `SqlServer` | `<your-server>.database.windows.net` |
| `WorkspaceId` | GUID of the `Retail Data` workspace |
| `LakehouseId` | GUID of the lakehouse |

This dataflow is per-lakehouse: make a copy of `df_erp_weather` for `lh_retail_sample` with
its own `LakehouseId`.

Weather comes from `erp.weather_daily`, which `retail_pipeline weather` fills from the
Open-Meteo archive API before `erp-load`. The dataflow itself makes no web calls: on the F2
capacity, Dataflow Gen2 failed every `Web.Contents` call to the API with a generic evaluation
error, while the same request worked from the local pipeline.

Weather data: Open-Meteo.com (CC BY 4.0).
