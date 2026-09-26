# Persona walkthrough

The plan was a usability test with five independent participants. Recruiting them isn't
possible for now, so the report is evaluated with a **persona walkthrough**. Someone signs in as
each of the four test accounts and works through the tasks each persona needs to answer, in the
published app. This checks that each persona can find and read its answers within its own
security view. It isn't an independent usability study: the evaluator knows the report. Findings
are recorded as such.

## Accounts

| Persona | Test account | App reports |
|---|---|---|
| Store manager | `store.manager@` | Store today (on a phone), Store performance, Fresh and availability |
| Regional manager | `regional.manager@` | Network overview, Store performance, Fresh and availability |
| Category manager | `category.manager@` | Network overview, Fresh and availability, Promotions |
| Head office | `head.office@` | All five |

## How to run it

1. Sign in to the app in a private browser window as the persona. For task 1, use the Power BI
   mobile app or a phone-sized window.
2. For each task, note:
   - where you started;
   - each click, filter or drill;
   - the time until the answer was on screen;
   - anything that slowed you down or could be misread.
3. Compare the answer with the answer key below. A task passes when the report shows the key's
   answer, is readable in the persona's view, and is reached in under a minute.
4. Record the results in `results.md`, and add each problem to the
   [v2 backlog](../report-v2-backlog.md).

## Tasks and answer key

"This year" is 2017, which is January to 15 August 2017, the last day in the data. The answers
were computed on Prod (full data) by impersonating each account through the Power BI API
(`service-check`), so they already reflect row-level security.

| # | Persona | Task | Answer key | Story |
|---|---|---|---|---|
| 1 | Store manager (phone) | "How did your store do on the last day in the report, against its target?" | Store 44 (Quito), 15 Aug 2017: Sales Value $108,422 against a target of $110,988, ▼ 2.3% | US-01 |
| 2 | Store manager | "Which fresh item looks most out of stock in your store over the last 7 days?" | Item 871513 (BREAD/BAKERY), about $473 estimated lost sales | US-02 |
| 3 | Regional manager | "Which of your stores is furthest behind on like-for-like sales this year?" | Store 2 (Quito), LFL ▼ 2.7% | US-04 |
| 4 | Regional manager | "For that store, is it fewer shoppers or smaller baskets?" | Both, mostly smaller baskets: footfall ▼ 0.7%, basket ▼ 2.0% | US-05, US-06 |
| 5 | Category manager | "Which product family gained most from promotions this year, and did sales drop afterwards?" | School and office supplies (uplift ▲ 1,149%, post-promo dip ▼ 5.8%). The uplift comes from a very small baseline, see backlog #6 | US-07 |
| 6 | Head office | "Which region is weakest against plan this year?" | Guayaquil at ▲ 3.2% vs target. No region is below plan in 2017 | US-09 |
