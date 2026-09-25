# Data profile

Measured on the real Favorita data (Kaggle download, `train.csv` 5.0 GB) with the local
pipeline, on a Windows laptop. Every data check passed on both builds.

## Builds

| | Full | Sample |
|---|---|---|
| Command | `build --raw data/raw --out data/full` | `… --out data/sample --sample` |
| Run time | 2 min 04 s | 13 s |
| Stores | 54 | 6 |
| Days (`dim_date`) | 1,688 (2013-01-01 to 2017-08-15) | 592 (2016-01-02 to 2017-08-15) |
| Items (`stg_item` / sold) | 4,100 / 4,036 | 4,100 / 4,017 |
| Store-days (`stg_store_day`) | 83,488 | 3,530 |
| `fact_sales` rows | 125,497,040 | 8,410,563 |
| `fact_stockout_risk` rows | 2,922,881 | 394,956 |
| DuckDB warehouse | 2.1 GB | — |
| Gold Parquet (`fact_sales`) | 494 MB | 31 MB |

Sample stores, the top 3 by receipts from 2016 in each city:

- Quito: 44, 45 and 47 (all type A).
- Guayaquil: 51 (A), 34 (B) and 24 (D).

Store 44 is the busiest Quito store, so it is the store manager's test store
([security](security.md)).

## What the data looks like

- **Promotions:** `onpromotion` is empty until 2014-03-31. 21.7M sales rows have an unknown
  promotion flag and 7.8M rows are on promotion. The promotion analysis therefore starts in
  April 2014.
- **Closures:** no store trades on 25 December. On 1 January only store 25 trades (plus store 36 in
  2014), and no store trades on 1 January 2016.
- **Opening dates:** 46 stores trade from the first week of the data, so their opening date is
  blank ("open before 2013") and they always count as like-for-like. Eight stores opened later:

  | Store | City | Opened |
  |---|---|---|
  | 36 | Libertad | 2013-05-09 |
  | 53 | Manta | 2014-05-29 |
  | 20 | Quito | 2015-02-13 |
  | 29 | Guayaquil | 2015-03-20 |
  | 21 | Santo Domingo | 2015-07-24 |
  | 42 | Cuenca | 2015-08-21 |
  | 22 | Puyo | 2015-10-09 |
  | 52 | Manta | 2017-04-20 |
- **Returns:** 7,795 rows with negative units (143,581 units) are kept separately in
  `return_units` and excluded from `Units`.

## Known gaps and how they are handled

- **Sales without receipts (118 store-days):** 109 of them fall on 2–4 January 2016, when
  `transactions.csv` is missing rows for almost every store. Those days have sales but no
  receipts, so Basket Value is undefined for them and footfall is undercounted for early
  January 2016. There are no store-days with receipts but no sales.
- **Partial trading days are not stock-out evidence:** on 119 store-days a store traded far
  below normal. Examples:
  - store 45 on 2017-04-03: 292 receipts against about 3,700;
  - store 53 in Manta on 17–18 April 2016, after the earthquake.

  Counting such a day as a full trading day flagged every item that didn't sell: 28,098 extra
  flags, with spikes of up to 1,504 on a single store-day. The stock-out rule therefore only
  flags days on which the store's receipts reach at least half of its average over the
  previous 28 days. After this change the busiest store-day has 323 flags.
- **Stock-out risk after peaks:** the expected rate λ averages the previous 28 trading days.
  The early-January flags therefore include items whose December demand didn't carry into
  January: the ten most-flagged dates are all in January 2017. The median is 89 flags per
  store-day, against about 1,900 items sold per store-day.
