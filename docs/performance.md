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

## Still to do (Phase 4)

- Cold and warm server timings in DAX Studio. It gives storage-engine and formula-engine splits and
  can clear the cache, which the REST API can't.
- The storage-mode comparison from [ADR-003](decisions/ADR-003-storage-mode-by-benchmark.md):
  Import (above) vs a composite model with aggregations vs Direct Lake.
- Optimise the two slow queries, re-run, and record before and after here.
