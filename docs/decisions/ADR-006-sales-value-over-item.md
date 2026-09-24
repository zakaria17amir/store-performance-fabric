# ADR-006: Sales value iterates Item

- Status: Accepted (2026-09-24)

## Context
Sales Value can be computed by storing a precomputed column on the ~125M-row Sales fact table,
multiplying units by price on every row, or by a measure that multiplies by a price stored once
per item. The two approaches will be compared in the Phase 4 benchmark (ADR-003).

## Decision
Store unit price and unit cost once on the Item table (about 4,000 rows) and compute
`Sales Value` as `SUMX('Item', [Units] * 'Item'[Unit Price])`, iterating Item rather than Sales.

## Consequences
+ The iteration runs over ~4,000 items instead of ~100M fact rows.
+ No precomputed column to store and refresh on the fact table.
− The SUMX-over-a-dimension pattern is less obvious than a plain SUM; the KPI glossary carries
  the explanation next to the DAX.
