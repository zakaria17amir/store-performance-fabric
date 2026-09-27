# Persona walkthrough: results

Run on 2026-09-27 in the published app `Store Performance Cockpit` (Prod, full data), following
the [protocol](protocol.md). The evaluator was the project author, signed in as each of the four
test accounts. This isn't an independent usability study: the evaluator knows the report.

| # | Persona | Task | Result |
|---|---|---|---|
| 1 | Store manager (phone) | Last day in the report vs target | Pass: the expected answer (Store 44, ▼ 2.3% vs target) |
| 2 | Store manager | Fresh item most likely out of stock, last 7 days | Pass: the expected answer (item 871513, Bread/Bakery) |
| 3 | Regional manager | Store furthest behind on like-for-like sales in 2017 | Pass: the expected answer (Store 2, ▼ 2.7%) |
| 4 | Regional manager | Fewer shoppers or smaller baskets for that store | Pass: the expected answer (both, mostly baskets) |
| 5 | Category manager | Family that gained most from promotions in 2017 | Pass: the expected answer (Grocery I, about 5.0M extra units) |
| 6 | Head office | Region weakest against plan in 2017 | Pass: the expected answer (Guayaquil, ▲ 3.2%) |

**6 of 6 tasks passed.** Each persona saw only its audience's reports, and the numbers matched the
answer key computed on Prod by impersonation.

Time on task and friction points weren't recorded in this run. The open usability items are the
ones in the [v2 backlog](../report-v2-backlog.md), found when the v1 pages were reviewed. An
independent test with people who don't know the report remains the next step when participants are
available.
