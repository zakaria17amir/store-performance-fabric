"""Checks against the published semantic model, through the Power BI executeQueries REST API.

- benchmark: warm timings of the heaviest report queries (median of several runs)
- rls: rows and columns each test user can see, by impersonating them
- totals: the model's units and sales per year and region against the lakehouse SQL endpoint
"""
import json
import math
import statistics
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API = "https://api.powerbi.com/v1.0/myorg"
PBI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"
SQL_SCOPE = "https://database.windows.net/.default"
ATTEMPTS = 3  # connection-level retries for a flaky uplink; query errors are never retried
CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"  # Microsoft's public Azure CLI client, as azure-identity uses

# The heaviest query behind each report page, as the visuals send it (period "All", no slicers).
BENCHMARK_QUERIES = {
    "network KPIs": "EVALUATE ROW(\"sales\", [Sales Value], \"vsTarget\", [Sales vs Target %], \"lfl\", [LFL Growth %], "
                    "\"footfall\", [LFL Footfall Growth %], \"basket\", [LFL Basket Growth %])",
    "region table": "EVALUATE SUMMARIZECOLUMNS('Store'[Region], \"sales\", [Sales Value], \"vsTarget\", [Sales vs Target %], "
                    "\"lfl\", [LFL Growth %], \"footfall\", [LFL Footfall Growth %], \"basket\", [LFL Basket Growth %])",
    "sales trend vs last year": "EVALUATE SUMMARIZECOLUMNS('Date'[Year], 'Date'[Month], 'Time Calc'[Show As], "
                                "TREATAS({\"Actual\", \"PY\"}, 'Time Calc'[Show As]), \"sales\", [Sales Value])",
    "store LFL split": "EVALUATE SUMMARIZECOLUMNS('Store'[Store], \"lfl\", [LFL Growth %], "
                       "\"footfall\", [LFL Footfall Growth %], \"basket\", [LFL Basket Growth %])",
    "items at risk": "EVALUATE TOPN(50, SUMMARIZECOLUMNS('Store'[Store], 'Item'[Item Number], 'Item'[Family], "
                     "TREATAS({TRUE}, 'Item'[Is Perishable]), \"units\", [Est. Lost Units], \"sales\", [Est. Lost Sales]), "
                     "[sales], DESC)",
    "promotions by family": "EVALUATE SUMMARIZECOLUMNS('Item'[Family], \"uplift\", [Promo Uplift %], "
                            "\"dip\", [Post-promo Dip %], \"margin\", [Gross Margin %])",
}
RLS_SCOPE = "EVALUATE ROW(\"stores\", COUNTROWS('Store'), \"accessRows\", COUNTROWS('User Access'))"
RLS_COST = "EVALUATE ROW(\"cost\", [Cost Value])"
TOTALS_DAX = "EVALUATE SUMMARIZECOLUMNS('Date'[Year], 'Store'[Region], \"units\", [Units], \"sales\", [Sales Value])"
TOTALS_SQL = """
SELECT d.year, s.region, SUM(f.units), SUM(f.units * i.unit_price)
FROM dbo.fact_sales f
JOIN dbo.dim_date d ON d.date_key = f.date_key
JOIN dbo.dim_store s ON s.store_key = f.store_key
JOIN dbo.dim_item i ON i.item_key = f.item_key
GROUP BY d.year, s.region
"""


class QueryError(RuntimeError):
    """The service refused or failed a query (for example OLS, or the per-query memory limit)."""


def token_provider(tenant: str, cache: Path):
    """Browser sign-in (with MFA) the first time, then silent refresh from an encrypted local cache."""
    import msal
    from msal_extensions import PersistedTokenCache, build_encrypted_persistence

    app = msal.PublicClientApplication(CLIENT_ID, authority=f"https://login.microsoftonline.com/{tenant}",
                                       token_cache=PersistedTokenCache(build_encrypted_persistence(str(cache))))

    def get(scope: str) -> str:
        accounts = app.get_accounts()
        result = (app.acquire_token_silent([scope], account=accounts[0]) if accounts else None) \
            or app.acquire_token_interactive([scope])
        if "access_token" not in result:
            raise RuntimeError(result.get("error_description", "sign-in failed"))
        return result["access_token"]

    return get


def sql_credential(token):
    """An azure-identity style credential for mssql_python's token_provider."""
    from azure.core.credentials import AccessToken

    class Credential:
        def get_token(self, *scopes, **kwargs):
            return AccessToken(token(SQL_SCOPE), int(time.time()) + 3000)

    return Credential()


def power_bi(token: str, opener=urlopen, wait_s: float = 5):
    """call(path) GETs, call(path, body) POSTs; service errors become QueryError."""

    def call(path: str, body: dict | None = None) -> dict:
        request = Request(f"{API}/{path}", data=json.dumps(body).encode() if body is not None else None,
                          headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        for attempt in range(ATTEMPTS):
            try:
                with opener(request, timeout=600) as response:
                    return json.load(response)
            except HTTPError as e:
                raise QueryError(e.read().decode(errors="replace")) from e
            except URLError:
                if attempt == ATTEMPTS - 1:
                    raise
                time.sleep(wait_s)

    return call


def dataset_id(call, workspace: str) -> str:
    return call(f"groups/{workspace}/datasets")["value"][0]["id"]


def run_dax(call, dataset: str, query: str, user: str | None = None) -> list[dict]:
    body = {"queries": [{"query": query}], "serializerSettings": {"includeNulls": True}}
    if user:
        body["impersonatedUserName"] = user
    result = call(f"datasets/{dataset}/executeQueries", body)["results"][0]
    if "error" in result:
        raise QueryError(json.dumps(result["error"]))
    return result["tables"][0]["rows"]


def benchmark(call, dataset: str, queries: dict[str, str], runs: int = 5, clock=time.perf_counter) -> dict[str, int]:
    """Median wall time in ms per query, after one warm-up run. Includes the REST round trip."""
    medians = {}
    for name, query in queries.items():
        run_dax(call, dataset, query)  # warm the cache
        timings = []
        for _ in range(runs):
            start = clock()
            run_dax(call, dataset, query)
            timings.append(clock() - start)
        medians[name] = round(statistics.median(timings) * 1000)
    return medians


def rls_matrix(call, dataset: str, users: list[str]) -> list[dict]:
    rows = []
    for user in users:
        scope = run_dax(call, dataset, RLS_SCOPE, user)[0]
        try:
            run_dax(call, dataset, RLS_COST, user)
            cost_visible = True
        except QueryError:  # object-level security removes Unit Cost, so the measure can't be evaluated
            cost_visible = False
        rows.append({"user": user, "stores": scope["[stores]"], "accessRows": scope["[accessRows]"] or 0,
                     "costVisible": cost_visible})
    return rows


def model_totals(call, dataset: str) -> dict[tuple, tuple]:
    return {(r["Date[Year]"], r["Store[Region]"]): (r["[units]"], r["[sales]"])
            for r in run_dax(call, dataset, TOTALS_DAX)}


def lakehouse_totals(cursor) -> dict[tuple, tuple]:
    cursor.execute(TOTALS_SQL)
    return {(year, region): (float(units), float(sales)) for year, region, units, sales in cursor.fetchall()}


def compare_totals(model: dict[tuple, tuple], lakehouse: dict[tuple, tuple]) -> list[tuple]:
    """Cells whose values differ beyond floating-point noise, or that exist on one side only."""
    mismatches = []
    for key in sorted(set(model) | set(lakehouse)):
        a, b = model.get(key), lakehouse.get(key)
        if a is None or b is None or not all(math.isclose(x, y, rel_tol=1e-9) for x, y in zip(a, b)):
            mismatches.append((key, a, b))
    return mismatches
