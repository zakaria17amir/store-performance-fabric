# ADR-001: Hybrid lakehouse

- Status: Accepted (2026-09-24)

## Context
~125M sales rows need heavy window logic; the Fabric trial is time-limited; the design must scale later.

## Decision
Prepare the large Favorita files locally with Python + DuckDB SQL and upload gold Delta tables to a Fabric lakehouse. Small external sources (Azure SQL, weather API) go through Dataflow Gen2.

## Consequences
+ Heavy processing is free and doesn't use trial capacity; SQL is testable in CI.
+ The gold table contract lets a Fabric notebook or Databricks replace DuckDB later.
− Two runtimes and an upload step to operate.
