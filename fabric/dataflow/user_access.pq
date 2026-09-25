let
    Source = Table.RenameColumns(src_Erp("user_access"), {{"store_nbr", "store_key"}}),
    Result = Table.SelectColumns(
        Table.NestedJoin(Source, {"store_key"}, src_Lakehouse("stg_store"), {"store_key"}, "s", JoinKind.Inner),
        {"user_principal_name", "store_key"})
in
    Result
