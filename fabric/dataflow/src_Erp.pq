// src_Erp: a table from the Azure SQL ERP schema
(name as text) as table => Sql.Database(SqlServer, "retail-erp"){[Schema = "erp", Item = name]}[Data]
