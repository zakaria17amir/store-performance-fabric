# Dataflow Gen2: df_erp_weather

Paste each `.pq` file into a blank query with the same name (without `.pq`).
Set the three parameters first. Destinations: every query without `_` in its name loads to
the `lh_retail` (or `lh_retail_sample`) lakehouse, table name = query name, replace mode.
Helper queries (`fn_*`, `src_*`) have load disabled.

| Parameter | Value |
|---|---|
| `SqlServer` | `<your-server>.database.windows.net` |
| `WorkspaceId` | GUID of the `Retail Data` workspace |
| `LakehouseId` | GUID of the lakehouse |

Weather data: Open-Meteo.com (CC BY 4.0).
