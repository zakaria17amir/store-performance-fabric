# ADR-009: Separate data and content workspaces

- Status: Accepted (2026-09-24)

## Context
The lakehouse and Dataflow Gen2 are shared by every deployment stage, while the semantic model
and report move through Dev, Test and Prod independently.

## Decision
Keep the lakehouse(s) and Dataflow Gen2 in a single `Retail Data` workspace, separate from the
`Retail BI Dev`, `Retail BI Test` and `Retail BI Prod` workspaces that hold the semantic model
and report.

## Consequences
+ One data layer is shared across all three content stages; no duplicated lakehouses.
+ Deployment pipelines only promote report and model content, matching how Fabric deployment
  rules work.
− An extra workspace to manage permissions and access for.
