"""Write gold Parquet files as Delta tables: a local folder or a lakehouse Tables/ ABFS path."""
from pathlib import Path

import pyarrow.dataset as ds
from deltalake import write_deltalake

STORAGE_SCOPE = "https://storage.azure.com/.default"


def onelake_options() -> dict[str, str]:
    # optional "azure" extra: imported only when needed
    from azure.identity import InteractiveBrowserCredential

    token = InteractiveBrowserCredential().get_token(STORAGE_SCOPE).token
    return {"bearer_token": token, "use_fabric_endpoint": "true"}


def publish(gold_dir: Path, target: str, storage_options: dict[str, str] | None = None) -> list[str]:
    """Overwrite one Delta table per gold Parquet file (atomic per table)."""
    tables = []
    for parquet in sorted(gold_dir.glob("*.parquet")):
        write_deltalake(f"{target.rstrip('/')}/{parquet.stem}", ds.dataset(parquet).scanner().to_reader(),
                        mode="overwrite", schema_mode="overwrite", storage_options=storage_options)
        tables.append(parquet.stem)
    return tables
