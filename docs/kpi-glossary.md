# KPI glossary

| KPI | Business meaning | Definition (DAX) |
|---|---|---|
| Units | Items sold (returns are kept in a separate column) | `SUM('Sales'[Unit Sales])` |
| Sales Value | Revenue at list price (synthetic prices) | `SUMX('Item', [Units] * 'Item'[Unit Price])` |
| Cost Value | Cost of goods sold (restricted) | `SUMX('Item', [Units] * 'Item'[Unit Cost])` |
| Gross Margin % | Share of revenue kept after cost of goods | `DIVIDE([Sales Value] - [Cost Value], [Sales Value])` |
| Receipts | Footfall: number of shopping trips | `SUM('Store Day'[Receipt Count])` |
| Basket Value | Average spend per trip | `DIVIDE([Sales Value], [Receipts])` |
| Target | Planned sales value, allocated to days | `SUM('Store Day'[Target Value])` |
| Sales vs Target % | Over/under plan | `DIVIDE([Sales Value] - [Target], [Target])` |
| LFL Growth % | Growth of stores open ≥ 12 months before the period, vs. same period last year | `LFL Sales` = Sales Value where `'Store'[Opening Date] <= EDATE(MIN('Date'[Date]), -12)`; growth vs. `SAMEPERIODLASTYEAR` for the same store set. Stores trading since the data starts have a blank Opening Date and always count as like-for-like. |
| LFL Footfall / Basket Growth % | Which lever drives LFL growth | Footfall: the same pattern on Receipts. Basket: `DIVIDE(sales growth − footfall growth, 1 + footfall growth)`, from (1 + sales growth) = (1 + footfall growth) × (1 + basket growth) |
| Fresh Share % | Perishables' share of revenue | Sales Value of perishable items ÷ all items |
| Promo Uplift % | Extra units on promotion days vs. the normal rate | `DIVIDE([Units] - [Baseline Units], [Baseline Units])` over promotion rows with a baseline > 0 |
| Post-promo Dip % | Sales lost in the 7 days after a promotion | Same formula over post-promotion rows with a baseline > 0 |
| Stock-out Risk Items | Store-item pairs with an improbable zero-sale day | `COUNTROWS(SUMMARIZE('Stock-out Risk', StoreKey, ItemKey))`: distinct flagged pairs |
| Est. Lost Units / Sales | Expected sales that did not happen on flagged days | `SUM('Stock-out Risk'[Expected Units])`, valued at unit price |

## Notes

- Basket Value, Sales vs Target % and LFL Basket Growth % combine Sales (which follows item/family filters) with Store Day (receipts and targets have no item grain). Under an item or family filter, only the sales side is filtered.
- The Time Calc items YoY Δ and YoY % applied to a ratio measure (e.g. Gross Margin %) give the change of the ratio: YoY Δ in percentage points, YoY % as relative change.
