# ADR-005: Dynamic RLS and OLS

- Status: Accepted (2026-09-24)

## Context
Store and regional managers must see only their own stores (US-10), and unit cost must stay
hidden from Store operations while remaining visible to Commercial. The store list changes over
time and shouldn't require adding a role per store or region.

## Decision
Add a hidden `User Access` table, unrelated to the rest of the model, holding user principal name
and store number. The Store operations role filters `Store[StoreKey]` to the rows in
`User Access` matching `USERPRINCIPALNAME()`. The same role applies OLS to hide
`Item[Unit Cost]`. The Commercial role has no row filter and no OLS.

## Consequences
+ Adding or moving a store is a data change in `User Access`, not a model or role change.
+ No bi-directional relationships needed to filter Store from an unrelated table.
− Row filtering depends on `USERPRINCIPALNAME()` matching exactly what's loaded into `User Access`.
