# ADR-011: Paid F2 capacity instead of the Fabric trial

- Status: Accepted (2026-09-25)

## Context
The plan assumed a free 60-day Fabric trial capacity. When the tenant was set up, Microsoft
refused the trial for it ("A Fabric trial isn't available for your account"). The only
subscription available is Azure for Students. Its policy allows five regions:

| Region | What it can host |
|---|---|
| Austria East, Belgium Central | Power BI only (no lakehouses) |
| Germany West Central | Nothing for Fabric: the subscription has a quota of 0 CU there |
| Poland Central, Sweden Central | Fabric, with a quota of 4 CU |

The Azure SQL free offer isn't available in Austria East either.

## Decision
- **Fabric:** buy a pay-as-you-go **F2** capacity (`fabretailpl`) in **Poland Central** and
  pause it whenever it's idle. It costs about $0.36 per running hour.
- **Tenant:** its home region stays Switzerland North, so the tenant is multi-geo. Workspace
  data lives in Poland Central.
- **Azure SQL:** `retail-erp` runs on the **Basic** tier in Austria East, the region its
  server was created in.

## Consequences
+ Everything the design needs runs on F2: lakehouses, Dataflow Gen2, pipelines, deployment
  pipelines, Git integration and Direct Lake.
+ There's no 60-day deadline. The capacity runs only while it's being worked on, so the cost
  stays at a few dollars.
+ The ERP adds only a small fixed cost: about $5 a month for the Basic tier. It is well
  within its 2 GB limit, since the ERP holds under 50,000 rows.
− F2 is below F64, so everyone who views a report needs a Power BI Pro or trial licence,
  including the test users. Free viewers aren't possible.
− F2 has a 3 GB memory limit per semantic model. An Import model of the full 125M-row
  `fact_sales` may not fit, or may not refresh. The ADR-003 benchmark measures this rather than
  assuming it: if Import doesn't fit, the options are the composite model or Direct Lake.
− A paused capacity can't serve anything: the SQL endpoint, refresh and reports all stop.
  Screenshots and the video are captured while it runs, and the sample Import model still
  opens offline in Desktop.
− Multi-geo: the tenant's metadata stays in Switzerland North while the data sits in Poland
  Central. Nothing in this project depends on where the data sits.
