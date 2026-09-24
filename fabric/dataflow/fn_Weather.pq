// Daily weather for one location from the Open-Meteo archive API.
(latitude as number, longitude as number) as table =>
let
    Response = Web.Contents(
        "https://archive-api.open-meteo.com",
        [
            RelativePath = "v1/archive",
            Query = [
                latitude = Number.ToText(latitude, "0.0000", "en-US"),
                longitude = Number.ToText(longitude, "0.0000", "en-US"),
                start_date = "2013-01-01",
                end_date = "2017-08-31",
                daily = "precipitation_sum,temperature_2m_max",
                timezone = "America/Guayaquil"
            ],
            ManualStatusHandling = {429, 500, 502, 503, 504}
        ]
    ),
    Status = Value.Metadata(Response)[Response.Status],
    Json = if Status = 200 then Json.Document(Response)
           else error Error.Record("WeatherApiError", "HTTP " & Text.From(Status)),
    Daily = Json[daily],
    Result = Table.Buffer(Table.FromColumns(
        {List.Transform(Daily[time], Date.FromText), Daily[precipitation_sum], Daily[temperature_2m_max]},
        type table [date = date, rain_mm = nullable number, temp_max_c = nullable number]))
in
    Result
