# Report v2 backlog

Issues found by reviewing the v1 pages on full data (exports in `docs/images/report/`) and while
preparing the [persona walkthrough](usability/protocol.md). Walkthrough findings get added here too,
and v2 works through the list.

| # | Page | Issue | Planned change |
|---|---|---|---|
| 1 | All | With the period on "All", comparisons mix complete and partial years, and the weekday chart's last-year bars cover a shorter span | Default the period slicer to the latest full year, or show "Year to date" by default |
| 2 | Network overview | The monthly trend shows 56 months with a scrollbar, and the y-axis labels ($0.0bn / $0.1bn) are too coarse | Start at year level and drill down to months; format the axis in $M |
| 3 | Network overview | The region table cuts off its third row | Grow the table or shrink the row height so all four regions show |
| 4 | Store performance, Fresh | Long subtitles are truncated ("right-click a store → Drill through → Sto…") | Shorten them; move the drill-through hint into a tooltip |
| 6 | Promotions | Promo Uplift % by family is led by small non-food families with tiny baselines (school supplies ▲ 1,149% in 2017), which hides the food families that matter | Rank families by extra units, not %, or set a minimum baseline; show the uplift % as a secondary value |
| 5 | Performance | "Sales trend vs last year" (~1.2 s) and "Items at risk" (~0.65 s) miss the 500 ms target | See [performance](performance.md): year-level default, top-N at query level |
