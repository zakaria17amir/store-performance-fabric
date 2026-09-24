import argparse
import json
from pathlib import Path

from .build import build
from .config import BuildConfig, sample_config


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="retail_pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build", help="raw CSVs → checked gold Parquet")
    b.add_argument("--raw", type=Path, default=Path("data/raw"))
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--sample", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "build":
        cfg = sample_config(args.raw, args.out) if args.sample else BuildConfig(args.raw, args.out)
        print(json.dumps(build(cfg), indent=2))


if __name__ == "__main__":
    main()
