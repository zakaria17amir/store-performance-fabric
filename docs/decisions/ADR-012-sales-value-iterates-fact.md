# ADR-012: Sales value iterates the fact table

- Status: Accepted (2026-09-26). Supersedes [ADR-006](ADR-006-sales-value-over-item.md).

## Context
ADR-006 computed `Sales Value` as `SUMX('Item', [Units] * 'Item'[Unit Price])`, iterating ~4,100
items. The first full-data queries in `Retail BI [Test]` on the F2 capacity showed its cost. To price
units per item, the engine first materialises units per item for every cell of the visual. A month ×
Time Calc (Actual vs PY) trend chart hit F2's **1 GB per-query memory limit** ("Resources Exceeded",
1,072 MB).

The same queries were run against the Test model through the Power BI `executeQueries` API,
with the alternative measure defined in the query:

| Query (full data, 125M sales rows) | Iterate Item | Iterate Sales with `RELATED` price |
|---|---|---|
| Sales by month × Time Calc (trend chart) | Fails: over 1 GB | 1.8 s |
| Region table (sales, vs target, LFL) | 1.7–3.9 s | 0.6–0.9 s |
| Store LFL ranking | 1.3 s | 0.7 s |
| Items at risk (store × item) | 1.1 s | 0.7 s |

Both versions return identical values ($3,703,710,874.81 in total).

## Decision
Compute value measures row by row on their fact table, with the price looked up through the
relationship:
- `Sales Value = SUMX('Sales', 'Sales'[Unit Sales] * RELATED('Item'[Unit Price]))`
- `Cost Value` does the same with `Unit Cost`.
- `Est. Lost Sales = SUMX('Stock-out Risk', 'Stock-out Risk'[Expected Units] * RELATED('Item'[Unit Price]))`

## Consequences
+ The storage engine computes the product during its scan, so there's no per-item intermediate
  result. Memory stays flat whatever the visual's grain, and the tested queries run 2–4 times
  faster.
+ No precomputed value column on the fact table, as ADR-006 also wanted.
− The row-level form scans every fact row in the filter context. Phase 4 (ADR-003) benchmarks it
  against Import alternatives on full data.
