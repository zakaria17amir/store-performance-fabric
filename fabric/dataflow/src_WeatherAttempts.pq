// One archive call per store city, 15 s apart (Open-Meteo free limits). Flat columns so staging can be on
// and both consumers read one staged copy. A city missing from city_geo (null latitude) becomes an error row.
let
    StoreCities = Table.Distinct(Table.SelectColumns(src_Lakehouse("stg_store"), {"city"})),
    WithGeo = Table.ExpandTableColumn(
        Table.NestedJoin(StoreCities, {"city"}, src_Erp("city_geo"), {"city"}, "g", JoinKind.LeftOuter),
        "g", {"latitude", "longitude"}),
    Attempts = Table.AddColumn(WithGeo, "attempt",
        each try Function.InvokeAfter(() => fn_Weather([latitude], [longitude]), #duration(0, 0, 0, 15))),
    Rows = Table.AddColumn(Attempts, "rows", each
        if [attempt][HasError]
        then #table(
            type table [date = nullable date, rain_mm = nullable number, temp_max_c = nullable number, error = nullable text],
            {{null, null, null, [attempt][Error][Message]}})
        else Table.AddColumn([attempt][Value], "error", each null, type nullable text)),
    Expanded = Table.ExpandTableColumn(Table.SelectColumns(Rows, {"city", "rows"}), "rows",
        {"date", "rain_mm", "temp_max_c", "error"}),
    Result = Table.TransformColumnTypes(Expanded, {
        {"city", type text}, {"date", type date}, {"rain_mm", type number}, {"temp_max_c", type number}, {"error", type text}})
in
    Result
