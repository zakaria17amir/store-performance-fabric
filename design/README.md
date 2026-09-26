# Report design

The design lives in Figma: [Store Performance Cockpit – Report design](https://www.figma.com/design/nO3cIoiq22TiEOd6QO0DE6/Store-Performance-Cockpit-%E2%80%93-Report-design?node-id=0-1).
PNG exports of each frame are in `wireframes/`.

![Network overview wireframe](wireframes/1-network-overview.png)

## Wireframes v1

Each page answers its personas' questions from the [requirements](../docs/requirements.md).

| Frame | For | User stories |
|---|---|---|
| [1 Network overview](wireframes/1-network-overview.png) | Head office, regional managers | US-09 |
| [2 Store performance](wireframes/2-store-performance.png) | Regional managers | US-04, US-05 |
| [2a Store detail (drill-through)](wireframes/2a-store-detail.png) | Regional managers | US-06 |
| [3 Fresh and availability](wireframes/3-fresh-and-availability.png) | Store managers, category managers | US-02 |
| [4 Promotions](wireframes/4-promotions.png) | Category managers | US-07, US-08 (margin: Commercial role only) |
| [5 Phone](wireframes/5-phone.png) | Store managers | US-01, US-02, US-03 |

The canvas is 1280 × 720 on an 8-px grid, with 16 px margins and gutters. Visual titles ask
the question the visual answers, and subtitles give the measure, unit and period. The values in
the wireframes are illustrative.

## Design tokens (theme v2)

`store-performance-theme.json` is the Power BI theme. v2 adds colour after the v1 review
("too colourless"). The Figma token sheet ([v1](wireframes/design-tokens.png)) shows the first,
mostly grey version.

The chart colours follow a validated categorical palette. Its order is part of the
colour-blind safety, so series always take slots in order. Checks use `validate_palette.js`
against the white card surface: CVD ΔE ≥ 9.1 between neighbours, normal-vision ΔE ≥ 19.6.

| Role | Colour | Contrast | Use |
|---|---|---|---|
| Series 1 · this year · positive | `#2a78d6` | 4.4:1 (marks) | Main series, bars at or above zero |
| Series 2 · last year / target | `#eb6834` | 3.2:1 (marks) | Comparison series |
| Negative | `#e34948` | 4.0:1 (marks) | Bars below zero (blue ↔ red diverging pair) |
| Header band, titles, KPI values | `#0d366b` | 11.9:1 | Page header (white text on it), visual titles |
| KPI tile | `#e8f1fc` | – | Card background; values 10.5:1, labels 7.0:1 |
| Table header | `#1c5cab` | 6.6:1 (white text) | Column headers |
| Page | `#eef2f8` | – | Canvas behind the white visuals |
| Text / secondary | `#0b0b0b` / `#52514e` | 17.5:1 / 7.9:1 | Values, labels, axes |

Series 3–8 (`#1baf7a`, `#eda100`, `#e87ba4`, `#008300`, `#4a3aa7`, `#e34948`) are for charts
with more series. Three of them are below 3:1 on white, so a chart using them needs data labels
or a table view.

Colour is never the only signal: ▲ and ▼ are in the growth measures' format strings, so every
label repeats the sign that the bar colour shows.
