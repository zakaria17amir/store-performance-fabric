# ADR-008: PBIP in Git with BPA in CI

- Status: Accepted (2026-09-24)

## Context
`main` only changes through pull requests with green CI. A Power BI binary file gives no
reviewable diff and no automated quality check.

## Decision
Store the semantic model and report as PBIP — TMDL for the model, PBIR for the report —
committed to Git, with the Best Practice Analyzer running in CI on every pull request.

## Consequences
+ Model and report changes get reviewable text diffs instead of an opaque binary file.
+ CI blocks a pull request that fails BPA rules, so quality issues don't reach `main`.
− CI depends on Tabular Editor 2 (Windows-only runner). It is pinned to 2.29.0 by checksum; if a
  TMDL change breaks it, the documented fallback is storing the model as `model.bim`.
