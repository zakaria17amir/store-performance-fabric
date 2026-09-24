let
    Cities = src_Erp("city_geo"),
    Attempts = Table.AddColumn(Cities, "attempt", each try fn_Weather([latitude], [longitude]))
in
    Attempts
