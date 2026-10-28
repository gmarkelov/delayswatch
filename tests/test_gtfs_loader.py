from pathlib import Path

import pandas as pd

import pytest

from app.gtfs_loader import load_gtfs_data


def test_load_gtfs_data(tmp_path: Path):
    gtfs = load_gtfs_data(Path("data/gtfs"))

    assert gtfs.keys() == {"stops", "routes", "trips", "stop_times"}
    assert all(
        isinstance(dataframe, pd.DataFrame) for dataframe in gtfs.values()
    )

def test_load_gtfs_data_missing_files(tmp_path: Path):
    with pytest.raises(FileNotFoundError) as exc_info:
        load_gtfs_data(tmp_path)

    assert str(exc_info.value) == (
        "Missing GTFS files: stops.txt, routes.txt, trips.txt, stop_times.txt"
    )