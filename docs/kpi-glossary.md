# KPI glossary

| KPI | Business meaning | Definition (DAX) |
|---|---|---|
| Units | Items sold, net of returns handled separately | `SUM(Sales[Units])` |
| Sales Value | Revenue at list price (synthetic prices) | `SUMX('Item', [Units] * 'Item'[Unit Price])` |
| Cost Value | Cost of goods sold (restricted) | `SUMX('Item', [Units] * 'Item'[Unit Cost])` |
| Gross Margin % | Share of revenue kept after cost of goods | `DIVIDE([Sales Value] - [Cost Value], [Sales Value])` |
| Receipts | Footfall: number of shopping trips | `SUM('Store Day'[Receipts])` |
| Basket Value | Average spend per trip | `DIVIDE([Sales Value], [Receipts])` |
| Target | Planned sales value, allocated to days | `SUM('Store Day'[Target Value])` |
| Sales vs Target % | Over/under plan | `DIVIDE([Sales Value] - [Target], [Target])` |
| LFL Growth % | Growth of stores open ≥ 12 months before the period, vs. same period last year | Calculated over the LFL store set (defined in Phase 2) |
| LFL Footfall / Basket Growth % | Which lever drives LFL growth | (1 + sales growth) = (1 + footfall growth) × (1 + basket growth) |
| Fresh Share % | Perishables' share of revenue | Sales Value of perishable items ÷ all items |
| Promo Uplift % | Extra units on promotion days vs. the normal rate | `DIVIDE(SUM(Units − Baseline), SUM(Baseline))` on promo rows |
| Post-promo Dip % | Sales lost in the 7 days after a promotion | Same formula on post-promotion rows |
| Stock-out Risk Items | Store-item pairs with an improbable zero-sale day | `DISTINCTCOUNT` of flagged pairs |
| Est. Lost Units / Sales | Expected sales that did not happen on flagged days | `SUM('Stock-out Risk'[Expected Units])`, valued at unit price |
