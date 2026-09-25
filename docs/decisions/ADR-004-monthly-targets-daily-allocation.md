# ADR-004: Monthly targets, daily allocation

- Status: Accepted (2026-09-24)

## Context
Real ERPs set sales targets monthly, so `sales_target_month` holds one row per store and month.
But the store manager's daily "yesterday vs. target" view (US-01) needs a target for every day.

## Decision
Keep targets at the monthly grain and allocate them to days with a T-SQL view
(`erp.v_sales_target_day`), splitting each month's target across days in proportion to the
store's weekday weights — each weekday's historical share of that store's sales value. The daily
values sum back exactly to the monthly target.

## Consequences
+ ERP data matches how targets are actually set; no synthetic daily target table to maintain.
+ Daily figures stay internally consistent — they always reconcile to the month.
− Adds a SQL view and a dependency on the weekday weights being computed correctly.
