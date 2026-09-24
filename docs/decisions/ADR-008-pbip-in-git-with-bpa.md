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
− TMDL support in Tabular Editor 2 is in preview; `model.bim` is the documented fallback for the
  CI check if it's needed.
