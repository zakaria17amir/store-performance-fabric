# Power BI project

Open `StorePerformance.pbip` in Power BI Desktop. `StorePerformance.SemanticModel/` is the semantic
model `Store Performance`, stored as TMDL. `StorePerformance.Report/` is the report, stored as PBIR.
`dataflow/` holds the Dataflow Gen2 queries.

## Model

| Table | Lakehouse source | Grain |
|---|---|---|
| Date | `dim_date` | 1 row per day (marked as the date table); `Calendar` hierarchy Year → Quarter → Month → Date |
| Store | `dim_store` | 1 row per store |
| Item | `dim_item` | 1 row per item |
| Sales | `fact_sales` | store × item × day |
| Store Day | `fact_store_day` | store × day |
| Stock-out Risk | `fact_stockout_risk` | store × item × flagged day |
| Time Calc | calculation group | Actual, MTD, YTD, PY, PY YTD, YoY Δ, YoY % |

Import mode reads the lakehouse SQL analytics endpoint. Two parameters choose the source:

| Parameter | Value |
|---|---|
| `SqlEndpoint` | SQL analytics endpoint host of the `Retail Data` workspace |
| `Lakehouse` | `lh_retail_sample` (Dev, Desktop) or `lh_retail` (Test, Prod: set by a deployment rule) |

Measure definitions are in the [KPI glossary](../docs/kpi-glossary.md). A pytest check
(`pipeline/tests/test_model_contract.py`) fails if the model reads a table outside the
[lakehouse contract](../docs/architecture.md#lakehouse-table-contract) or a gold column that doesn't exist.

## Fabric setup

- **Git integration:** `Retail BI [Dev]` syncs with branch `main`, folder `fabric/`. Fabric reads only
  the folders that have a `.platform` file (the model and the report), and it ignores `dataflow/`
  and `bpa/`.
- **Refresh connection:** the service won't refresh an Import model through the default Single
  Sign-On connection (`Premium_ASWL_Error`). Each lakehouse needs an explicit cloud connection
  (type SQL Server, OAuth 2.0), mapped under semantic model settings → Gateway and cloud
  connections:
  - `sql-lh-retail-sample` is used by Dev.
  - `sql-lh-retail` is used by Test and Prod.
- **Deployment pipeline `Store Performance release`:** Development (`Retail BI [Dev]`) → Test →
  Production. A parameter rule on the Test and Production stages sets `Lakehouse` to `lh_retail`,
  so only Dev reads the sample. Rules take effect on the next deploy.
- **Dataflows:** `df_erp_weather_sample` writes to `lh_retail_sample` and `df_erp_weather` writes to
  `lh_retail`. They run the same queries; only the `LakehouseId` parameter and the destinations
  differ.
- **Refresh:** the data pipeline `pl_refresh` in `Retail Data` runs the dataflow, then refreshes the
  semantic model. It uses a *Power BI Semantic Model* connection (`pbi-semantic-models`, OAuth 2.0).
  There's no schedule, because the capacity is paused when idle. There's also no failure email,
  because the admin account has no mailbox; failures show in the Monitoring hub.
- **SQL endpoint sign-in:** the SQL analytics endpoint reads OneLake as its owner. When the
  owner's Entra token goes stale, every read fails with `AdalMultiFactorAuthException`. Signing in
  to Fabric again with MFA fixes it. If it doesn't, use **Take over** in the SQL analytics endpoint's
  settings.
- **Desktop:** save once after the first refresh. The data is then cached in `.pbi/cache.abf`
  (ignored by Git), and the project reopens without refreshing.

## Quality gate

On every pull request, CI runs Tabular Editor 2's Best Practice Analyzer against two rule sets:

- Microsoft's standard rules, in `bpa/microsoft-rules.json`. This is a copy of
  [microsoft/Analysis-Services](https://github.com/microsoft/Analysis-Services/tree/master/BestPracticeRules)
  (MIT), pinned at commit `50e8ce5`.
- The project rules, in `bpa/project-rules.json`: descriptions, display folders and
  single-direction relationships.

Any severity-3 violation fails the build. To run it locally (Windows, PowerShell 7):

```powershell
./fabric/bpa/run-bpa.ps1 -TabularEditor <path to TabularEditor.exe>
```
