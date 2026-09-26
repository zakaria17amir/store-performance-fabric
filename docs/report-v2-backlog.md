# Report v2 backlog

Issues found by reviewing the v1 pages on full data (exports in `docs/images/report/`) and while
preparing the [persona walkthrough](usability/protocol.md). Walkthrough findings get added here too,
and v2 works through the list.

| # | Page | Issue | Change | Status |
|---|---|---|---|---|
| 1 | All | With the period on "All", comparisons mix complete and partial years, and the weekday chart's last-year bars cover a shorter span | The period slicers default to 2017 (the drill-through page inherits the source page's filters) | Done in v2 (2026-09-26) |
| 2 | Network overview | The monthly trend shows 56 months with a scrollbar, and the y-axis labels ($0.0bn / $0.1bn) are too coarse | With the 2017 default the trend shows 8 months; the axis is in $M | Done in v2 (2026-09-26) |
| 3 | Network overview | The region table cuts off its third row | Charts 24 px shorter, table taller: all four regions and the total show | Done in v2 (2026-09-26) |
| 4 | Store performance, Fresh | Long subtitles are truncated ("right-click a store → Drill through → Sto…") | Subtitles wrap on every visual | Done in v2 (2026-09-26) |
| 6 | Promotions | Promo Uplift % by family is led by small non-food families with tiny baselines (school supplies ▲ 1,149% in 2017), which hides the food families that matter | New measure `Promo Extra Units`; the family bar ranks by it and shows uplift % in the tooltip | Done in v2 (2026-09-26) |
| 5 | Performance | "Sales trend vs last year" (~1.2 s) and "Items at risk" (~0.65 s) miss the 500 ms target | See [performance](performance.md): year-level default, top-N at query level | Open (Phase 4) |
