import argparse
import json
from pathlib import Path

from .build import build
from .config import BuildConfig, sample_config
from .erp_seed import write_erp_seed
from .extract import extract_archives
from .geo import write_city_geo
from .publish import onelake_options, publish


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
    s.add_argument("--seed", type=int, default=42)

    g = sub.add_parser("geo", help="store-city coordinates → city_geo.csv")
    g.add_argument("--warehouse", type=Path, required=True)
    g.add_argument("--out", type=Path, required=True)

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
        print(json.dumps(write_erp_seed(args.warehouse, args.out, args.seed), indent=2))
    if args.command == "geo":
        print(write_city_geo(args.warehouse, args.out), "cities located")


if __name__ == "__main__":
    main()
