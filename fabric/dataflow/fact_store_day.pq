let
    DateKey = (d as date) as number => Date.Year(d) * 10000 + Date.Month(d) * 100 + Date.Day(d),
    Receipts = src_Lakehouse("stg_store_day"),
    TargetsRaw = src_Erp("v_sales_target_day"),
    Targets = Table.FromRecords(Table.TransformRows(TargetsRaw, each [
        date_key = DateKey(Date.From([target_date])), store_key = [store_nbr], target_value = [target_value]])),
    Joined = Table.NestedJoin(Receipts, {"date_key", "store_key"}, Targets, {"date_key", "store_key"}, "t", JoinKind.FullOuter),
    Expanded = Table.ExpandTableColumn(Joined, "t", {"date_key", "store_key", "target_value"}, {"t_date_key", "t_store_key", "target_value"}),
    Keys = Table.AddColumn(Table.AddColumn(Expanded,
        "dk", each if [date_key] = null then [t_date_key] else [date_key], Int64.Type),
        "sk", each if [store_key] = null then [t_store_key] else [store_key], Int64.Type),
    Tidy = Table.RenameColumns(Table.SelectColumns(Keys, {"dk", "sk", "receipts", "target_value"}),
        {{"dk", "date_key"}, {"sk", "store_key"}}),
    // keep only this lakehouse's stores and dates (the ERP holds targets for all 54 stores and all years)
    DateKeys = src_Lakehouse("dim_date")[date_key],
    MinDateKey = List.Min(DateKeys),
    MaxDateKey = List.Max(DateKeys),
    InDateRange = Table.SelectRows(Tidy, each [date_key] >= MinDateKey and [date_key] <= MaxDateKey),
    Cities = Table.SelectColumns(src_Lakehouse("stg_store"), {"store_key", "city"}),
    WithCity = Table.ExpandTableColumn(
        Table.NestedJoin(InDateRange, {"store_key"}, Cities, {"store_key"}, "c", JoinKind.Inner), "c", {"city"}),
    Weather = Table.SelectColumns(Table.SelectRows(src_WeatherAttempts, each [error] = null), {"city", "date", "rain_mm", "temp_max_c"}),
    WeatherKeyed = Table.RemoveColumns(Table.AddColumn(Weather, "date_key", each DateKey([date]), Int64.Type), {"date"}),
    WithWeather = Table.ExpandTableColumn(
        Table.NestedJoin(WithCity, {"city", "date_key"}, WeatherKeyed, {"city", "date_key"}, "w", JoinKind.LeftOuter),
        "w", {"rain_mm", "temp_max_c"}),
    Result = Table.TransformColumnTypes(Table.RemoveColumns(WithWeather, {"city"}), {
        {"receipts", Int64.Type}, {"target_value", Currency.Type}, {"rain_mm", type number}, {"temp_max_c", type number}})
in
    Result
