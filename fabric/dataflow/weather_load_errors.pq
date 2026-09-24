let
    Failed = Table.SelectRows(src_WeatherAttempts, each [attempt][HasError]),
    Errors = Table.AddColumn(Failed, "error", each [attempt][Error][Message], type text),
    Result = Table.TransformColumnTypes(Table.SelectColumns(Errors, {"city", "error"}), {{"city", type text}})
in
    Result
