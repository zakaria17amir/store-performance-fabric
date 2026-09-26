import argparse
import json
from pathlib import Path

from .build import build
from .config import BuildConfig, sample_config
from .erp_load import connect_azure_sql, load_erp
from .erp_seed import write_erp_seed
from .extract import extract_archives
from .geo import write_city_geo, write_weather
from .publish import onelake_options, publish
from . import service


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="retail_pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build", help="raw CSVs → checked gold Parquet")
    b.add_argument("--raw", type=Path, default=Path("data/raw"))
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--sample", action="store_true")
    b.add_argument("--publish-to", help="Delta target: local folder or lakehouse Tables/ ABFS path")

    e = sub.add_parser("extract", help="unpack the Kaggle download")
    e.add_argument("--src", type=Path, default=Path("data/download"))
    e.add_argument("--dest", type=Path, default=Path("data/raw"))

    s = sub.add_parser("erp-seed", help="gold warehouse → synthetic ERP CSVs")
    s.add_argument("--warehouse", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    s.add_argument("--upn-domain", required=True, help="tenant domain of the test users, e.g. contoso.onmicrosoft.com")
    s.add_argument("--seed", type=int, default=42)

    g = sub.add_parser("geo", help="store-city coordinates → city_geo.csv")
    g.add_argument("--warehouse", type=Path, required=True)
    g.add_argument("--out", type=Path, required=True)

    w = sub.add_parser("weather", help="city_geo.csv → daily weather per city (weather_daily.csv)")
    w.add_argument("--csv", type=Path, required=True, help="folder with city_geo.csv; the output goes there too")

    el = sub.add_parser("erp-load", help="schema + synthetic ERP CSVs → Azure SQL")
    el.add_argument("--server", required=True)
    el.add_argument("--database", default="retail-erp")
    el.add_argument("--csv", type=Path, required=True)
    el.add_argument("--sql", type=Path, default=Path("erp"))

    sc = sub.add_parser("service-check", help="benchmark, RLS matrix or totals against a published semantic model")
    sc.add_argument("check", choices=["benchmark", "rls", "totals"])
    sc.add_argument("--workspace", required=True, help="workspace ID that holds the semantic model")
    sc.add_argument("--tenant", required=True, help="Entra tenant ID or domain")
    sc.add_argument("--token-cache", type=Path, default=Path.home() / ".retail-pipeline-tokens.bin")
    sc.add_argument("--runs", type=int, default=5)
    sc.add_argument("--users", help="comma-separated user principal names (rls)")
    sc.add_argument("--sql-endpoint", help="lakehouse SQL analytics endpoint host (totals)")
    sc.add_argument("--lakehouse", help="lakehouse name, e.g. lh_retail (totals)")

    args = parser.parse_args(argv)
    if args.command == "build":
        cfg = sample_config(args.raw, args.out) if args.sample else BuildConfig(args.raw, args.out)
        counts = build(cfg)  # raises on failed checks, so nothing is published after a failure
        print(json.dumps(counts, indent=2))
        if args.publish_to:
            options = onelake_options() if args.publish_to.startswith("abfss://") else None
            print("published:", ", ".join(publish(cfg.out_dir / "gold", args.publish_to, options)))
    if args.command == "extract":
        for path in extract_archives(args.src, args.dest):
            print(path)
    if args.command == "erp-seed":
        print(json.dumps(write_erp_seed(args.warehouse, args.out, args.upn_domain, args.seed), indent=2))
    if args.command == "geo":
        print(write_city_geo(args.warehouse, args.out), "cities located")
    if args.command == "weather":
        print(write_weather(args.csv), "city-days of weather")
    if args.command == "erp-load":
        con = connect_azure_sql(args.server, args.database)
        try:
            print(json.dumps(load_erp(con, args.csv, args.sql), indent=2))
        finally:
            con.close()

    if args.command == "service-check":
        token = service.token_provider(args.tenant, args.token_cache)
        call = service.power_bi(token(service.PBI_SCOPE))
        dataset = service.dataset_id(call, args.workspace)
        if args.check == "benchmark":
            result = service.benchmark(call, dataset, service.BENCHMARK_QUERIES, args.runs)
        elif args.check == "rls":
            result = service.rls_matrix(call, dataset, args.users.split(","))
        else:
            import mssql_python

            con = mssql_python.connect(f"Server=tcp:{args.sql_endpoint},1433;Database={args.lakehouse};Encrypt=yes;",
                                       token_provider=service.sql_credential(token))
            try:
                mismatches = service.compare_totals(service.model_totals(call, dataset),
                                                    service.lakehouse_totals(con.cursor()))
            finally:
                con.close()
            result = {"mismatches": [[list(k), a, b] for k, a, b in mismatches]}
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
