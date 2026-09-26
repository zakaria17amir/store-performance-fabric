# KPI glossary

| KPI | Business meaning | Definition (DAX) |
|---|---|---|
| Units | Items sold (returns are kept in a separate column) | `SUM('Sales'[Unit Sales])` |
| Sales Value | Revenue at list price (synthetic prices) | `SUMX('Sales', 'Sales'[Unit Sales] * RELATED('Item'[Unit Price]))` (see ADR-012) |
| Cost Value | Cost of goods sold (restricted) | `SUMX('Sales', 'Sales'[Unit Sales] * RELATED('Item'[Unit Cost]))` |
| Gross Margin % | Share of revenue kept after cost of goods | `DIVIDE([Sales Value] - [Cost Value], [Sales Value])` |
| Receipts | Footfall: number of shopping trips | `SUM('Store Day'[Receipt Count])` |
| Basket Value | Average spend per trip | `DIVIDE([Sales Value], [Receipts])` |
| Target | Planned sales value, allocated to days | `SUM('Store Day'[Target Value])` |
| Sales vs Target % | Over/under plan | (Sales Value − Target) ÷ Target over the store-months that have a target. A store has no target before its first full prior-year month (all of 2013, each new store's first year), so those sales are left out rather than counted against a zero target. |
| LFL Growth % | Growth of stores open ≥ 12 months before the period, vs. same period last year | `LFL Sales` = Sales Value where `'Store'[Opening Date] <= EDATE(period start, -12)`; growth vs. `SAMEPERIODLASTYEAR` for the same store set. Only dates with a prior year in the data count (from one year after the first data date), so a period that starts earlier is compared on its comparable part only. The prior-year side never runs past the last data date minus one year: `SAMEPERIODLASTYEAR` would otherwise treat the data's last day (15 Aug 2017) as a month end and compare 1–15 Aug 2017 with all of August 2016. The Time Calc PY, PY YTD and YoY items use the same cap. Stores trading since the data starts have a blank Opening Date and always count as like-for-like. |
| LFL Footfall / Basket Growth % | Which lever drives LFL growth | Footfall: the same pattern on Receipts. Basket: `DIVIDE(sales growth − footfall growth, 1 + footfall growth)`, from (1 + sales growth) = (1 + footfall growth) × (1 + basket growth) |
| Fresh Share % | Perishables' share of revenue | Sales Value of perishable items ÷ all items |
| Promo Uplift % | Extra units on promotion days vs. the normal rate | `DIVIDE([Units] - [Baseline Units], [Baseline Units])` over promotion rows with a baseline > 0 |
| Post-promo Dip % | Sales lost in the 7 days after a promotion | Same formula over post-promotion rows with a baseline > 0 |
| Stock-out Risk Items | Store-item pairs with an improbable zero-sale day | `COUNTROWS(SUMMARIZE('Stock-out Risk', StoreKey, ItemKey))`: distinct flagged pairs |
| Est. Lost Units / Sales | Expected sales that did not happen on flagged days | `SUM('Stock-out Risk'[Expected Units])`, valued at unit price |
| Est. Lost Sales (7 days) | Est. Lost Sales in the 7 days up to the last selected date (phone view) | `DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -7, DAY)` |

## Notes

- Basket Value, Sales vs Target % and LFL Basket Growth % combine Sales (which follows item/family filters) with Store Day (receipts and targets have no item grain). Under an item or family filter, only the sales side is filtered.
- The Time Calc items YoY Δ and YoY % applied to a ratio measure (e.g. Gross Margin %) give the change of the ratio: YoY Δ in percentage points, YoY % as relative change.
- Avg Rain (mm) and Avg Max Temp (°C) average over store-day rows, so at region level a city with more stores weighs more.
