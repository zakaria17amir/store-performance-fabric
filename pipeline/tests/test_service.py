import io
from urllib.error import URLError

import pytest

from retail_pipeline.service import QueryError, benchmark, compare_totals, power_bi, rls_matrix, run_dax


class FakeApi:
    """Records executeQueries calls and answers from a script keyed by (query, user)."""

    def __init__(self, answers):
        self.answers, self.calls = answers, []

    def __call__(self, path, body=None):
        query, user = body["queries"][0]["query"], body.get("impersonatedUserName")
        self.calls.append((path, query, user))
        answer = self.answers[(query, user)]
        if isinstance(answer, Exception):
            raise answer
        return {"results": [{"tables": [{"rows": answer}]}]}


def test_run_dax_impersonates_the_user_and_returns_rows():
    api = FakeApi({("EVALUATE x", "a@b.c"): [{"[v]": 1}]})
    assert run_dax(api, "ds1", "EVALUATE x", user="a@b.c") == [{"[v]": 1}]
    assert api.calls == [("datasets/ds1/executeQueries", "EVALUATE x", "a@b.c")]


def test_benchmark_reports_the_median_of_the_timed_runs_after_a_warm_up():
    api = FakeApi({("EVALUATE q", None): [{"[v]": 1}]})
    ticks = iter([0, 1,  0, 3,  0, 2])  # 3 timed runs: 1 s, 3 s, 2 s (the warm-up isn't timed)
    result = benchmark(api, "ds1", {"q": "EVALUATE q"}, runs=3, clock=lambda: next(ticks))
    assert result == {"q": 2000}
    assert len(api.calls) == 4


def test_rls_matrix_marks_cost_hidden_when_the_query_is_refused():
    scope = "EVALUATE ROW(\"stores\", COUNTROWS('Store'), \"accessRows\", COUNTROWS('User Access'))"
    cost = "EVALUATE ROW(\"cost\", [Cost Value])"
    api = FakeApi({
        (scope, "store@x"): [{"[stores]": 1, "[accessRows]": 1}],
        (cost, "store@x"): QueryError("Column 'Unit Cost' cannot be found"),
        (scope, "head@x"): [{"[stores]": 54, "[accessRows]": None}],
        (cost, "head@x"): [{"[cost]": 100.0}],
    })
    assert rls_matrix(api, "ds1", ["store@x", "head@x"]) == [
        {"user": "store@x", "stores": 1, "accessRows": 1, "costVisible": False},
        {"user": "head@x", "stores": 54, "accessRows": 0, "costVisible": True},
    ]


def test_compare_totals_flags_cells_that_differ():
    model = {(2016, "Quito"): (10.0, 100.0), (2016, "Sierra"): (5.0, 50.0)}
    lakehouse = {(2016, "Quito"): (10.0, 100.0), (2016, "Sierra"): (5.0, 51.0), (2017, "Quito"): (1.0, 1.0)}
    assert compare_totals(model, lakehouse) == [
        ((2016, "Sierra"), (5.0, 50.0), (5.0, 51.0)),
        ((2017, "Quito"), None, (1.0, 1.0)),
    ]


def test_compare_totals_allows_rounding_noise():
    assert compare_totals({(2016, "Quito"): (10.0, 1e9)}, {(2016, "Quito"): (10.0, 1e9 + 0.01)}) == []


def test_query_error_carries_the_service_message():
    api = FakeApi({("EVALUATE bad", None): QueryError("Resources Exceeded")})
    with pytest.raises(QueryError, match="Resources Exceeded"):
        run_dax(api, "ds1", "EVALUATE bad")


def test_power_bi_retries_connection_errors_but_not_query_errors():
    attempts = []

    def flaky(request, timeout):
        attempts.append(request.full_url)
        if len(attempts) == 1:
            raise URLError("connection refused")
        return io.BytesIO(b'{"ok": true}')

    call = power_bi("token", opener=flaky, wait_s=0)
    assert call("groups") == {"ok": True}
    assert len(attempts) == 2
