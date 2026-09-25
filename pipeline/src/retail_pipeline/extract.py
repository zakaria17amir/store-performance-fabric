import zipfile
from pathlib import Path

import py7zr


def extract_archives(src: Path, dest: Path) -> list[Path]:
    """Unpack the Kaggle competition zip, then the .7z CSV archives inside it."""
    dest.mkdir(parents=True, exist_ok=True)
    for zip_path in src.glob("*.zip"):
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(dest)
    for archive in sorted(dest.glob("*.7z")):
        with py7zr.SevenZipFile(archive) as sz:
            sz.extractall(dest)
    return sorted(dest.glob("*.csv"))
