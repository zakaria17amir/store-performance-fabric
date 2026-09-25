let
    Staged = src_Lakehouse("stg_item"),
    Prices = Table.NestedJoin(Staged, {"item_nbr"}, src_Erp("item_price"), {"item_nbr"}, "p", JoinKind.LeftOuter),
    Result = Table.ExpandTableColumn(Prices, "p", {"unit_price", "unit_cost"})
in
    Result
