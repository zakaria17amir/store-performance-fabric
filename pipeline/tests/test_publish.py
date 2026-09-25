from deltalake import DeltaTable

from retail_pipeline.__main__ import main
from retail_pipeline.publish import publish


def test_publish_writes_every_gold_table(full_build, tmp_path):
    cfg, counts = full_build
    target = tmp_path / "Tables"
    assert sorted(publish(cfg.out_dir / "gold", str(target))) == sorted(counts)
    for table, rows in counts.items():
        assert DeltaTable(str(target / table)).to_pyarrow_table().num_rows == rows


def test_republish_overwrites(full_build, tmp_path):
    cfg, counts = full_build
    target = str(tmp_path / "Tables")
    publish(cfg.out_dir / "gold", target)
    publish(cfg.out_dir / "gold", target)
    table = DeltaTable(f"{target}/fact_sales")
    assert table.version() == 1
    assert table.to_pyarrow_table().num_rows == counts["fact_sales"]


def test_cli_build_then_publish(raw_dir, tmp_path):
    main(["build", "--raw", str(raw_dir), "--out", str(tmp_path / "out"), "--sample",
          "--publish-to", str(tmp_path / "Tables")])
    assert (tmp_path / "Tables" / "fact_sales" / "_delta_log").is_dir()
