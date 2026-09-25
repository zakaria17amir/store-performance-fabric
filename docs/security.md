# Security

The `Store Performance` semantic model has two roles. Roles decide which **data** a person
sees; Power BI app audiences decide which **pages** they see. For the design reasons, see
[ADR-005](decisions/ADR-005-dynamic-rls-and-ols.md).

## Roles

| Role | Row filter | Object-level security | Members |
|---|---|---|---|
| Store operations | Stores listed for the signed-in user in `User Access` | `'Item'[Unit Cost]` removed | Store managers, regional managers |
| Commercial | None | None | Category managers, head office |

Each person belongs to exactly one role. Row-level and object-level security from different roles can't be combined: Power BI returns an error at query time for anyone who is a member of both roles.

### Store operations: dynamic RLS

```dax
'Store'[StoreKey] IN
    CALCULATETABLE(
        VALUES('User Access'[StoreKey]),
        'User Access'[User Principal Name] = USERPRINCIPALNAME()
    )
```

- `User Access` has no relationship to `Store`. The rule reads it directly, so no
  bi-directional relationship is needed, and the `Store` filter reaches every fact table
  through the normal one-to-many relationships.
- One role serves every store and region, because access is data rather than roles. To give
  someone access, add rows to `erp.user_access`, then refresh the dataflow and the model.
- `User Access` is also filtered to the signed-in user's own rows, so nobody can list other
  people's access.
- Object-level security removes `'Item'[Unit Cost]`. Measures built on it (`Cost Value`,
  `Gross Margin %`) are unavailable to this role, so margin visuals only go on pages whose
  app audiences are commercial users.

### Commercial

This role sees all stores and all columns. `User Access` returns no rows (`FALSE()`), because
commercial users don't need the access list.

## Test users

| User | Role | Expected stores | Unit cost and margin | App audience |
|---|---|---|---|---|
| `store.manager@<domain>` | Store operations | 1: the busiest Quito store from 2016 onward | Hidden | Store managers |
| `regional.manager@<domain>` | Store operations | Every store in region Quito (Pichincha); 3 in the sample lakehouse | Hidden | Regional managers |
| `category.manager@<domain>` | Commercial | All | Visible | Category managers |
| `head.office@<domain>` | Commercial | All | Visible | Head office |

The ERP seed writes the `user_access` rows for the first two users:

```bash
python -m retail_pipeline erp-seed --warehouse data/full/warehouse.duckdb --out data/erp --upn-domain <tenant>.onmicrosoft.com
```

Create all four users in Microsoft Entra ID with these user principal names, and give them
app access only.
Create them as members of the tenant, not as B2B guests: a guest's `USERPRINCIPALNAME()` has the `#EXT#` form and won't match the seeded rows.

## How to test

- **Power BI Desktop:** Modeling → View as. Tick *Other user*, enter the user principal
  name, and tick the role.
- **Power BI service:** semantic model → Security → Test as role.
- Workspace Admins, Members and Contributors bypass RLS. Test users therefore get app access
  only, and security is never tested with a workspace member.

## Results

Desktop checks were run on 2026-09-25 against `lh_retail_sample` (6 stores, 3 of them in Quito),
with Modeling → View as. The test page had a table of stores with `Sales Value`, a table of
`User Access` (hidden columns shown), and a `Cost Value` card.

| Check | Desktop | Service |
|---|---|---|
| Store manager sees one store; `Unit Cost`, `Cost Value` and `Gross Margin %` unavailable | Pass: Store 44 only ($86.2M); the `Cost Value` card fails ([screenshot](images/security/desktop-store-manager.png)) | Pending |
| Regional manager sees only region Quito | Pass: stores 44, 45 and 47 ($241.4M); the `Cost Value` card fails ([screenshot](images/security/desktop-regional-manager.png)) | Pending |
| Category manager and head office see all stores and margin | Pass: all 6 stores ($341.4M); `Cost Value` $255M (screenshots: [category manager](images/security/desktop-commercial.png), [head office](images/security/desktop-head-office.png)) | Pending |
| No test user can list `User Access` rows other than their own | Pass: 1 row for the store manager, 3 for the regional manager, none for Commercial users | Pending |
| No test user is a member of both roles | Not applicable in Desktop, where View as picks the role | Pending |

The service checks follow once the model is published and the test users have app access.
