# Performance

Target from the spec: every visual's query runs in under 500 ms on a warm cache on full data.
All numbers below are for the full lakehouse (125M sales rows) on the F2 capacity
([ADR-011](decisions/ADR-011-paid-f2-capacity.md)), with the model in Import mode.

## Refresh

| Model | Data | Refresh |
|---|---|---|
| `Retail BI [Dev]` | Sample (6 stores, 2016 onward) | About 1.5 minutes |
| `Retail BI [Test]` | Full (54 stores, 2013 to mid-August 2017) | 13 minutes |

The full Import model fits F2's 3 GB model memory limit.

## Query memory: the value measures

F2 also caps each **query** at 1 GB. The first version of `Sales Value` iterated the ~4,100 items
(`SUMX('Item', [Units] * 'Item'[Unit Price])`), and the monthly trend chart (month × Time Calc
Actual/PY) failed with "Resources Exceeded" (1,072 MB). Computing the value row by row on the fact
table with the price looked up through the relationship fixed it and made every tested query faster
([ADR-012](decisions/ADR-012-sales-value-iterates-fact.md)):

| Query | Iterate Item | Iterate Sales with `RELATED` price |
|---|---|---|
| Sales by month × Time Calc | Fails: over 1 GB | 1.8 s |
| Region table | 1.7–3.9 s | 0.6–0.9 s |
| Store LFL ranking | 1.3 s | 0.7 s |
| Items at risk | 1.1 s | 0.7 s |

These times include the REST round trip; see the method below.

## Warm-query benchmark (v1, Import)

`python -m retail_pipeline service-check benchmark` sends the heaviest query behind each report page
to the published model through the Power BI `executeQueries` API. It runs each query once to warm
the cache, then times 5 runs and reports the median. That wall time includes the REST round trip
from the client, measured separately with a trivial query (`EVALUATE ROW("x", 1)`: median 555 ms
on the test connection). Subtracting it gives an estimate of the engine time.

Run on 2026-09-26 against `Retail BI [Test]` (full data, period "All"):

| Query (report page) | Median wall time | Estimated engine time | Under 500 ms? |
|---|---|---|---|
| Network KPIs (Network overview) | 623 ms | ~70 ms | Yes |
| Region table (Network overview) | 643 ms | ~90 ms | Yes |
| Promotions by family (Promotions) | 822 ms | ~270 ms | Yes |
| Store LFL split (Store performance) | 944 ms | ~390 ms | Yes |
| Items at risk (Fresh and availability) | 1,209 ms | ~650 ms | No |
| Sales trend vs last year (Network overview) | 1,796 ms | ~1,240 ms | No |

Two queries miss the target. The trend chart evaluates `Sales Value` for every month twice (Actual
and the capped PY item). The items-at-risk table ranks every store × perishable item pair. Both are
the starting points for Phase 4.

## Storage-mode comparison

Decided in [ADR-003](decisions/ADR-003-storage-mode-by-benchmark.md): **Import**.

Three variants of the same model ran in `Retail BI [Test]` on full data:
- **V1 Import:** the Prod model.
- **V3 Direct Lake:** built from the same TMDL through the Fabric API. Its partitions read the
  `lh_retail` Delta tables directly. `Date[Year Month]` and `Store[Store]` are left out, because
  they are derived in Power Query.
- **V2 composite:** facts in DirectQuery on the SQL endpoint, dimensions Import.

Direct Lake returned the same 2017 answers as Import: Sales vs Target, LFL and lost sales are
identical, and Sales Value differs by $4 on $645M from fixed-decimal rounding. The queries use
`Store[Store Number]` in place of the store label, so they run unchanged on both models.

Run on 2026-09-27, just after pausing and resuming the capacity to clear throttling. Median of 3
warm runs, wall time including the ~555 ms round trip:

| Query | V1 Import | V3 Direct Lake |
|---|---|---|
| Network KPIs | 591 ms | 1,647 ms |
| Region table | 550 ms | 2,040 ms |
| Sales trend vs last year | 749 ms | 1,244 ms |
| Store LFL split | 734 ms | 21,503 ms (throttled) |
| Items at risk | 785 ms | 20,826 ms (throttled) |
| Promotions by family | 670 ms | 22,611 ms (throttled) |

After subtracting the round trip, every Import query is under the 500 ms budget. The earlier
1.8 s and 1.2 s for the trend and items-at-risk queries (in the benchmark table above) were
measured while other work was loading the capacity.

Loading the Direct Lake columns into memory for the first time used enough compute to push F2
into throttling within minutes. Fabric then added a 20-second delay to every query, and next
rejected queries ("capacity has exceeded its limits"). An earlier session had also throttled F2,
when cold-cache runs in DAX Studio, a model refresh and benchmarking overlapped. Pausing and
resuming the capacity clears throttling and bills the borrowed compute.

**Lesson for F2:** run cold-cache benchmarks and first-time Direct Lake loads alone on the
capacity, not alongside development work.

The composite variant (V2) was built and refreshed but not benchmarked, because its queries scan
the fact table through the throttled SQL endpoint. ADR-003 explains why aggregations were left out.

## Cold cache (DAX Studio)

`fabric/benchmark/queries.dax` holds the same 6 queries for DAX Studio. Connect to
`powerbi://api.powerbi.com/v1.0/myorg/Retail BI [Test]`, turn on Server Timings, choose "Clear
cache then run", and run one query at a time. First result: the full batch took 22.9 s after
clearing the Import cache, and 0.5–0.7 s warm. Per-query storage-engine and formula-engine splits
are still to capture.
