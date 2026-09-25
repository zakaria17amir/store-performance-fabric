# Architecture

Store Performance Cockpit is a governed analytics product for the store network of a discount
grocery retailer. It uses real point-of-sale data from Corporación Favorita (Kaggle) as the
stand-in retailer. It combines three kinds of source (files, a SQL database and a REST API)
into one star-schema semantic model on Microsoft Fabric, secured per role and released
through Dev → Test → Prod.

The design rationale lives in [the design spec](design/2026-09-24-store-performance-design.md).
This page describes the system as built.

## Data flow

```mermaid
flowchart TB
    subgraph SRC[Sources]
        K["Favorita sales files<br/>Kaggle CSVs, ~125M rows"]
        S[("Azure SQL: retail-erp<br/>regions, prices, targets, access")]
        W["Open-Meteo archive API<br/>daily weather per city"]
    end
    subgraph LOCAL[Local machine]
        P["Local pipeline<br/>Python + DuckDB SQL<br/>bronze → silver → gold + data tests"]
    end
    subgraph DATA["Fabric workspace: Retail Data"]
        LH[("Lakehouses<br/>lh_retail (full) · lh_retail_sample<br/>Delta tables")]
        DF["Dataflow Gen2: df_erp_weather<br/>Power Query M"]
        PL["Data pipeline: pl_refresh"]
    end
    subgraph BI["Fabric workspaces: Retail BI Dev → Test → Prod"]
        SM["Semantic model: Store Performance<br/>star schema · calc group · RLS/OLS"]
        R["Report: Store Performance<br/>4 pages + phone layout"]
        APP["Power BI app<br/>one audience per persona"]
    end
    K --> P
    P -->|"Delta upload (only if tests pass)"| LH
    S --> DF
    W --> DF
    LH -->|"staged store, item, store-day tables"| DF
    DF -->|"conformed dimensions and facts"| LH
    PL -. "1. refresh" .-> DF
    PL -. "2. refresh" .-> SM
    LH --> SM --> R --> APP
```

| Component | Owns | Technology |
|---|---|---|
| Local pipeline | Favorita download, cleaning, the gold star schema, derived facts (promo baseline, stock-out risk), data tests, upload | Python, DuckDB SQL, pytest, Delta Lake |
| Azure SQL `retail-erp` | ERP-style master data: state → region, store profile, item price and cost, monthly targets, weekday weights, user → store access | Azure SQL Database (free offer), T-SQL |
| Dataflow Gen2 `df_erp_weather` | Conforms ERP attributes onto the staged dimensions, joins daily targets from the ERP view, loads weather | Power Query M |
| Data pipeline `pl_refresh` | Runs the dataflow, then refreshes the semantic model | Fabric Data Factory |
| Semantic model `Store Performance` | Star schema, measures, time-intelligence calculation group, RLS and OLS | Power BI (PBIP / TMDL) |
| Report and app | Four desktop pages, a phone layout, app audiences | Power BI (PBIR) |

## Lakehouse table contract

The gold tables are the interface between data preparation and the semantic model. Each
producer can be replaced (for example DuckDB → Fabric notebook or Databricks) without touching
the model, as long as these tables keep their grain and columns.

| Table | Produced by | Grain | Used by |
|---|---|---|---|
| `dim_date` | Local pipeline | 1 row per calendar day | Model |
| `stg_store` | Local pipeline | 1 row per store (Favorita attributes, first day with receipts (full history)) | Dataflow |
| `stg_item` | Local pipeline | 1 row per item | Dataflow |
| `stg_store_day` | Local pipeline | store × day (receipts) | Dataflow |
| `fact_sales` | Local pipeline | store × item × day (units, promo flag, baseline) | Model |
| `fact_stockout_risk` | Local pipeline | store × item × day, flagged days only | Model |
| `dim_store` | Dataflow | 1 row per store (+ region, selling area) | Model |
| `dim_item` | Dataflow | 1 row per item (+ unit price, unit cost) | Model |
| `fact_store_day` | Dataflow | store × day (receipts, daily target, weather) | Model |
| `user_access` | Dataflow | user × store | Model (RLS) |
| `weather_load_errors` | Dataflow | 1 row per failed API call | Monitoring |

## Semantic model

```mermaid
erDiagram
    DATE ||--o{ SALES : DateKey
    STORE ||--o{ SALES : StoreKey
    ITEM ||--o{ SALES : ItemKey
    DATE ||--o{ STORE_DAY : DateKey
    STORE ||--o{ STORE_DAY : StoreKey
    DATE ||--o{ STOCKOUT_RISK : DateKey
    STORE ||--o{ STOCKOUT_RISK : StoreKey
    ITEM ||--o{ STOCKOUT_RISK : ItemKey
    SALES {
        int DateKey FK
        int StoreKey FK
        int ItemKey FK
        decimal Units
        decimal BaselineUnits
        bool OnPromo
        bool PostPromoWindow
    }
    STORE_DAY {
        int DateKey FK
        int StoreKey FK
        int Receipts
        decimal TargetValue
        decimal RainMm
        decimal TempMaxC
    }
    STOCKOUT_RISK {
        int DateKey FK
        int StoreKey FK
        int ItemKey FK
        decimal ExpectedUnits
    }
    DATE {
        int DateKey PK
        date Date
        int Year
        string Month
        string Weekday
        bool IsNationalHoliday
    }
    STORE {
        int StoreKey PK
        string Store
        string City
        string State
        string Region
        string StoreType
        date OpeningDate
    }
    ITEM {
        int ItemKey PK
        string Family
        int Class
        bool IsPerishable
        decimal UnitPrice
        decimal UnitCost "OLS: hidden from Store operations"
    }
    USER_ACCESS {
        string UserPrincipalName
        int StoreKey "no relationship, read by the RLS rule"
    }
```

- All relationships are one-to-many, single direction, on integer keys. No bi-directional filtering.
- `USER_ACCESS` is deliberately unrelated: the RLS rule on `Store` reads it with
  `USERPRINCIPALNAME()`, which avoids bi-directional relationships.
- Time intelligence is a calculation group; a field parameter drives the metric switcher.

## Build and release

```mermaid
flowchart LR
    PR["Pull request<br/>feature branch"] --> CI["GitHub Actions<br/>pytest data tests · BPA check"]
    CI --> MAIN["main branch<br/>PBIP: TMDL + PBIR"]
    MAIN -->|Fabric Git integration| DEV["Retail BI [Dev]<br/>sample lakehouse"]
    DEV -->|deployment pipeline| TEST["Retail BI [Test]<br/>full data · checks"]
    TEST -->|deployment pipeline| PROD["Retail BI [Prod]<br/>app + audiences"]
```

| Workspace | Contents | Data |
|---|---|---|
| `Retail Data` | `lh_retail`, `lh_retail_sample`, `df_erp_weather`, `pl_refresh` | Full and sample |
| `Retail BI [Dev]` | Semantic model, report (Git-synced to `main`) | Sample lakehouse |
| `Retail BI [Test]` | Same items, promoted by the deployment pipeline | Full lakehouse |
| `Retail BI [Prod]` | Same items plus the Power BI app | Full lakehouse |

A deployment-pipeline data source rule points Dev at `lh_retail_sample` and Test/Prod at
`lh_retail`. Test users only get app access. Workspace members bypass RLS, so they are
never used to test security.

## Security

| Role | Row filter | Object-level security | Personas |
|---|---|---|---|
| Store operations | Stores listed for the user in `user_access` | `'Item'[Unit Cost]` hidden, so margin is unavailable | Store manager, regional manager |
| Commercial | None (all stores) | None | Category manager, head office |

App audiences decide which pages each persona sees. Roles decide which data they can see.

Role definitions, the RLS rule and the test matrix: [security.md](security.md).

## Scaling path

- **More data**: move the local pipeline into a Fabric notebook or Databricks. The table contract stays the same.
- **More sources**: add queries to the dataflow and conform them onto existing dimensions.
- **More reports**: build thin reports on the shared semantic model instead of new models.
- **More users**: add rows to `user_access`. No new roles are needed per region or store.

Weather data by [Open-Meteo.com](https://open-meteo.com/) (CC BY 4.0).
