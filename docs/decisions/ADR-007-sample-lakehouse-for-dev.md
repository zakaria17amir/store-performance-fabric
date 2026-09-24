# ADR-007: Sample lakehouse for Dev

- Status: Accepted (2026-09-24)

## Context
The sample dataset — six stores across two regions, from 2016-01-01 onward — is built by the
same pipeline with a `--sample` flag, and needs to feed the Dev workspace, Power BI Desktop
development and the offline demo.

## Decision
Point the Dev workspace and Power BI Desktop development at the sample lakehouse
(`lh_retail_sample`). Use a deployment rule to repoint the data source to the full lakehouse
(`lh_retail`) when promoting to Test and Prod.

## Consequences
+ Fast local iteration and a small model that opens offline in Desktop for the demo.
+ Two regions in the sample still let region-level RLS be demonstrated without full data.
− Dev and Desktop never see full-data volume or performance; that is the benchmark's job
  (ADR-003), not Dev.
