# ADR-003: Storage mode decided by benchmark

- Status: Accepted (2026-09-27): Import, decided by the Phase 4 benchmark below

## Context
The model must meet a 500 ms warm-cache budget per visual on full data (~125M sales rows).
Three storage modes are candidates for Prod: Import, a composite model with the Sales detail in
DirectQuery plus an imported store × family × day aggregation, and Direct Lake on OneLake. Direct
Lake supports no user-defined aggregations and needs Fabric capacity, so the right choice needs
measured evidence, not a guess.

## Decision
Develop against Import storage mode by default. Decide the Prod storage mode in Phase 4 from a
benchmark: 6 DAX queries taken from the heaviest visuals, each run 5 times cold and 5 times warm
in DAX Studio per variant (V1 Import, V2 composite, V3 Direct Lake), reporting median duration,
the formula-engine/storage-engine split and the storage-engine query count. The fastest variant
that meets the budget and the operating constraints goes to Prod.

## Consequences
+ The storage-mode decision rests on measured numbers, recorded alongside this record.
+ Import keeps Dev and Desktop simple until the benchmark runs.
− The Prod architecture isn't final until Phase 4; earlier work must not assume one mode.

## Outcome (2026-09-27)
Measured on the F2 capacity with full data (125M sales rows), with the same 6 queries through the
Power BI `executeQueries` API. Each figure is the median of 3 warm runs, as wall time including a
~555 ms REST round trip. Details are in [performance](../performance.md#storage-mode-comparison).

| Variant | Refresh | Warm queries | Capacity impact |
|---|---|---|---|
| V1 Import | 13 min | 0.55–0.79 s (all under the 500 ms engine budget) | Low |
| V3 Direct Lake | ~0.1 s (framing only) | 1.2–2.0 s for the first three queries | Loading columns into memory pushed F2 into throttling within minutes (20 s delays, then rejected queries) |
| V2 Composite | Dimensions only | Not measured | Every query scans the 125M-row fact table through the SQL endpoint, on the same throttled F2 |

**Decision: Prod uses Import.** It is the fastest, meets the budget, and uses the least capacity
per query. The 13-minute refresh is acceptable for a daily refresh.

**Direct Lake** would remove the refresh and suits larger capacities, where transcoding doesn't
throttle. Revisit it if the capacity grows or the data outgrows F2's 3 GB model memory.

**Composite with user-defined aggregations** wasn't built. Aggregations only cover plain `SUM`s
of columns, while the value measures are row-level `SUMX(… RELATED(price))` (ADR-012). They would
need a precomputed value column on the fact table. Revisit if Import stops fitting.

Cold-cache timings from DAX Studio are partial: the full 6-query batch took 22.9 s after
clearing the Import cache.
