import argparse
import json
from pathlib import Path

from .build import build
from .config import BuildConfig, sample_config
from .erp_seed import write_erp_seed
from .extract import extract_archives


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="retail_pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build", help="raw CSVs → checked gold Parquet")
    b.add_argument("--raw", type=Path, default=Path("data/raw"))
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--sample", action="store_true")

    e = sub.add_parser("extract", help="unpack the Kaggle download")
    e.add_argument("--src", type=Path, default=Path("data/download"))
    e.add_argument("--dest", type=Path, default=Path("data/raw"))

    s = sub.add_parser("erp-seed", help="gold warehouse → synthetic ERP CSVs")
    s.add_argument("--warehouse", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    s.add_argument("--seed", type=int, default=42)

    args = parser.parse_args(argv)
    if args.command == "build":
        cfg = sample_config(args.raw, args.out) if args.sample else BuildConfig(args.raw, args.out)
        print(json.dumps(build(cfg), indent=2))
    if args.command == "extract":
        for path in extract_archives(args.src, args.dest):
            print(path)
    if args.command == "erp-seed":
        print(json.dumps(write_erp_seed(args.warehouse, args.out, args.seed), indent=2))


if __name__ == "__main__":
    main()
