import logging

from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

GTFS_FILES = {
    "stops": "stops.txt",
    "routes": "routes.txt",
    "trips": "trips.txt",
    "stop_times": "stop_times.txt"
}

def load_gtfs_data(data_dir: Path) -> dict[str, pd.DataFrame]:
    logger.info(f"Loading GTFS data from {data_dir}")

    missing_files = [
        filename
        for filename in GTFS_FILES.values()
        if not (data_dir / filename).is_file()
    ]

    if missing_files:
        raise FileNotFoundError(
            f"Missing GTFS files: {', '.join(missing_files)}"
        )

    gtfs = {}

    for name, filename in GTFS_FILES.items():
        gtfs[name] = pd.read_csv(data_dir / filename)
        logger.info("Loaded %s: %s rows", filename, f"{len(gtfs[name]):,}")

    return gtfs