# ADR-010: Upstream-derived facts

- Status: Accepted (2026-09-24)

## Context
Promotion uplift and stock-out risk both need window logic — a 28-day trailing average per
store-item, evaluated per row — which is expensive to recompute in DAX at query time over the
full fact table.

## Decision
Compute the promotion baseline (28-day trailing average units per store-item) and the stock-out
risk flag, with its expected-units value, in the local SQL pipeline, and load them as gold
tables. The DAX measures (Promo Uplift %, Post-promo Dip %, Stock-out Risk Items, Est. Lost
Units / Sales) just aggregate these precomputed columns.

## Consequences
+ Heavy window-function logic runs once in SQL/DuckDB instead of per query in DAX.
+ DAX measures stay simple, which keeps them fast and easier to review against BPA rules.
− The pipeline owns this business logic; changing it needs a pipeline re-run and re-upload, not
  just a model edit.
