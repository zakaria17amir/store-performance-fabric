# ADR-002: Lakehouse-only model source

- Status: Accepted (2026-09-24)

## Context
The gold Favorita tables land in the lakehouse from the local DuckDB pipeline (ADR-001). The
ERP and weather data land there too, via Dataflow Gen2. The semantic model must work under
whichever storage mode the Phase 4 benchmark picks (ADR-003) — Import, a composite model with
DirectQuery, or Direct Lake.

## Decision
The semantic model reads only lakehouse tables, never Azure SQL or the Dataflow directly.
Dataflow Gen2 output lands in the lakehouse before the model touches it.

## Consequences
+ One ingestion path into the model regardless of storage mode; Import, DirectQuery and Direct
  Lake all read the same plain Delta tables.
+ Swapping storage modes for the Phase 4 benchmark doesn't touch the source tables.
− An extra landing step for data that could otherwise be queried directly, such as Azure SQL.
