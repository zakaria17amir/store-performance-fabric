# Power BI project

Open `StorePerformance.pbip` in Power BI Desktop. `StorePerformance.SemanticModel/` is the semantic
model `Store Performance`, stored as TMDL. `StorePerformance.Report/` is the report, stored as PBIR.
`dataflow/` holds the Dataflow Gen2 queries.

## Model

| Table | Lakehouse source | Grain |
|---|---|---|
| Date | `dim_date` | 1 row per day (marked as the date table) |
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
  - `lh_retail` needs its own connection for Test and Prod.
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
