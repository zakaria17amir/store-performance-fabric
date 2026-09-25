"""Write gold Parquet files as Delta tables: a local folder or a lakehouse Tables/ ABFS path."""
from pathlib import Path

import pyarrow.dataset as ds
from deltalake import write_deltalake

def onelake_options() -> dict[str, str]:
    # tokens come from `az login` and are refreshed during long uploads (a fixed bearer token expires after ~1 h);
    # a slow uplink can take longer than the 30 s default to send one upload block
    return {"use_azure_cli": "true", "use_fabric_endpoint": "true", "timeout": "600s"}


def publish(gold_dir: Path, target: str, storage_options: dict[str, str] | None = None) -> list[str]:
    """Overwrite one Delta table per gold Parquet file (atomic per table)."""
    tables = []
    for parquet in sorted(gold_dir.glob("*.parquet")):
        write_deltalake(f"{target.rstrip('/')}/{parquet.stem}", ds.dataset(parquet).scanner().to_reader(),
                        mode="overwrite", schema_mode="overwrite", storage_options=storage_options)
        tables.append(parquet.stem)
    return tables
