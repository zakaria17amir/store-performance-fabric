let
    Source = src_Erp("user_access"),
    Result = Table.RenameColumns(Source, {{"store_nbr", "store_key"}})
in
    Result
