let
    StoreCities = List.Distinct(src_Lakehouse("stg_store")[city]),
    Cities = Table.SelectRows(src_Erp("city_geo"), each List.Contains(StoreCities, [city])),
    Attempts = Table.AddColumn(Cities, "attempt", each try fn_Weather([latitude], [longitude]))
in
    Attempts
