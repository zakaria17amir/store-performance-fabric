let
    Staged = src_Lakehouse("stg_store"),
    Profile = Table.NestedJoin(Staged, {"store_nbr"}, src_Erp("store_profile"), {"store_nbr"}, "profile", JoinKind.LeftOuter),
    WithArea = Table.ExpandTableColumn(Profile, "profile", {"selling_area_m2"}),
    States = Table.NestedJoin(WithArea, {"state"}, src_Erp("state_region"), {"state"}, "sr", JoinKind.LeftOuter),
    WithRegionId = Table.ExpandTableColumn(States, "sr", {"region_id"}),
    Regions = Table.NestedJoin(WithRegionId, {"region_id"}, src_Erp("region"), {"region_id"}, "r", JoinKind.LeftOuter),
    WithRegion = Table.ExpandTableColumn(Regions, "r", {"region_name"}, {"region"}),
    Result = Table.RemoveColumns(WithRegion, {"region_id"})
in
    Result
