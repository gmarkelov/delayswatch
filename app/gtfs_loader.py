"""
Script to load GTFS data
"""

from pathlib import Path

import pandas as pd

GTFS_FILES = {
    "stops": "stops.txt",
    "routes": "routes.txt",
    "trips": "trips.txt",
    "stop_times": "stop_times.txt"
}

def load_gtfs_data(data_dir: Path) -> dict[str, pd.DataFrame]:
    """Loading GTFS data into dataframes."""

    missing_files = [
        filename
        for filename in GTFS_FILES.values()
        if not (data_dir / filename).is_file()
    ]

    if missing_files:
        raise FileNotFoundError(
            f"Missing GTFS files: {', '.join(missing_files)}"
        )

    return {
        name: pd.read_csv(data_dir / filename)
        for name, filename in GTFS_FILES.items()
    }