import zipfile

import py7zr

from retail_pipeline.extract import extract_archives


def test_extracts_zip_then_7z(tmp_path):
    csv_path = tmp_path / "stores.csv"
    csv_path.write_text("store_nbr\n1\n")
    with py7zr.SevenZipFile(tmp_path / "stores.csv.7z", "w") as archive:
        archive.write(csv_path, "stores.csv")
    with zipfile.ZipFile(tmp_path / "competition.zip", "w") as zf:
        zf.write(tmp_path / "stores.csv.7z", "stores.csv.7z")
    src = tmp_path / "download"
    src.mkdir()
    (tmp_path / "competition.zip").rename(src / "competition.zip")

    extracted = extract_archives(src, tmp_path / "raw")

    assert [p.name for p in extracted] == ["stores.csv"]
    assert (tmp_path / "raw" / "stores.csv").read_text() == "store_nbr\n1\n"
