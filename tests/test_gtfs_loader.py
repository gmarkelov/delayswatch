from pathlib import Path

import pandas as pd

from app.gtfs_loader import load_gtfs_data


def test_load_gtfs_data(tmp_path: Path):
    gtfs = load_gtfs_data(Path("data/gtfs"))

    assert gtfs.keys() == {"stops", "routes", "trips", "stop_times"}
    assert all(
        isinstance(dataframe, pd.DataFrame) for dataframe in gtfs.values()
    )

def test_load_gtfs_data_missing_file(tmp_path: Path):
    # Create a temporary directory with only some GTFS files
    (tmp_path / "stops.txt").write_text("stop_id,stop_name\n1,Stop A\n2,Stop B")
    (tmp_path / "routes.txt").write_text("route_id,route_name\n1,Route A\n2,Route B")

    try:
        load_gtfs_data(tmp_path)
    except FileNotFoundError as e:
        assert "Missing GTFS files" in str(e)