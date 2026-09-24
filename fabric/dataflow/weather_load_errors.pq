let
    Errors = Table.SelectRows(src_WeatherAttempts, each [error] <> null),
    Result = Table.TransformColumnTypes(Table.SelectColumns(Errors, {"city", "error"}), {{"city", type text}, {"error", type text}})
in
    Result
