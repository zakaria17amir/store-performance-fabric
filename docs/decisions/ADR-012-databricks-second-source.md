# ADR-012: Databricks as a second model source

- Status: Accepted (2026-09-28)

## Context
A companion project, [favorita-stockout-promo-databricks](https://github.com/zakaria17amir/favorita-stockout-promo-databricks),
rebuilds this repo's gold tables on Databricks Free Edition for the last 12 months and reconciles them with the
DuckDB build: identical sales rows, units and promotion baselines. It also produces analysis this model doesn't have:
- stock-out runs tested with a negative binomial at a 5% false discovery rate;
- promo events with uplift, the post-promotion dip and net lift;
- family-level bootstrap confidence intervals.

Power BI Desktop connects to its SQL warehouse with the **Azure Databricks** connector and a personal access token.
The plain *Databricks* connector needs OAuth on AWS. That test is recorded in the companion project's ADR-002.

## Decision
- Read five of its gold tables **directly** from the Databricks SQL warehouse, in Import mode, in every stage (Dev,
  Test, Prod). Two model parameters hold the host and HTTP path. They're the same in every stage, so no deployment
  rule is needed.
- The three fact tables relate to `Date`, `Store` and `Item`, so the existing Store row filter covers them. The two
  network-level tables (`Promo Payback`, `Stock-out Test`) are denied to `Store operations`.
- Show them in one new thin report, `DeepDive`, following the one-report-per-page rule. The existing reports and
  measures don't change.
- A contract test (`test_model_reads_only_documented_databricks_tables`) limits the model to the documented
  Databricks tables and columns.

## Consequences
+ The model now combines a Fabric lakehouse with a Databricks warehouse, and store security reaches both.
+ The deep-dive statistics stay in the project that computes and tests them. This model only reads them.
− **An Import refresh refreshes every table.** If the Databricks source fails, the whole Store Performance model
  fails to refresh, not just the new report. Causes include an expired token, the free workspace being paused by
  its daily compute cap, or the account being removed after long inactivity. For a demo whose capacity is paused
  and refreshed by hand this is acceptable. For production use, land the tables in the lakehouse instead: the
  companion project's notebook 07 exports them as Parquet.
− The Service needs one more cloud connection (Azure Databricks, personal access token), mapped in each workspace.
  The token expires and must be renewed.
− The Databricks tables cover 2016-08-16 → 2017-08-15 only. The deep-dive report shows that window, while the
  other reports show the full history.
− Dev and Desktop read the 6-store sample lakehouse, but Databricks holds all 54 stores. Rows for the other stores
  have no `Store` match. The store visuals filter out the blank store, and a row filter hides such rows anyway.
