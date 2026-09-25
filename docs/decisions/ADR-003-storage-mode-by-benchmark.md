# ADR-003: Storage mode decided by benchmark

- Status: Proposed (decided in Phase 4 by benchmark)

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
