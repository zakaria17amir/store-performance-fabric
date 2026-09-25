from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class BuildConfig:
    raw_dir: Path
    out_dir: Path
    sample: bool = False
    start_date: date = date(1900, 1, 1)
    stockout_from: date = date(2016, 1, 1)
    lookback_days: int = 28
    min_expected_units: float = 3.0
    min_receipts_share: float = 0.5  # of the store's trailing average
    post_promo_days: int = 7

    @property
    def db_path(self) -> Path:
        return self.out_dir / "warehouse.duckdb"


def sample_config(raw_dir: Path, out_dir: Path) -> BuildConfig:
    """Six stores (top 3 in Quito and Guayaquil) from 2016 onward."""
    return BuildConfig(raw_dir=raw_dir, out_dir=out_dir, sample=True, start_date=date(2016, 1, 1))
