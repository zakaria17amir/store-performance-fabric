// src_Lakehouse: a table from the lakehouse
(name as text) as table =>
    Lakehouse.Contents(null){[workspaceId = WorkspaceId]}[Data]{[lakehouseId = LakehouseId]}[Data]{[Id = name, ItemKind = "Table"]}[Data]
