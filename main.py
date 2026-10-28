import logging
from pathlib import Path

from app import railway_graph
from app.gtfs_loader import load_gtfs_data
from app.gtfs_processor import filter_irish_rail_data, build_trip_patterns, build_hub_network
from app.railway_graph import build_railway_graph, plot_railway_graph

from app.logger_config import setup_logging

logger = logging.getLogger(__name__)

def main() -> None:
    setup_logging()
    logger.info("Starting GTFS preparation")

    gtfs = load_gtfs_data(Path("data/gtfs"))
    ir_gtfs = filter_irish_rail_data(gtfs)

    trips_with_patterns, trip_patterns = build_trip_patterns(
        ir_gtfs["trips"],
        ir_gtfs["stop_times"],
    )

    hub_stations, hub_edges = build_hub_network(
        ir_gtfs["stops"],
        trip_patterns,
    )

    logger.info("GTFS preparation completed")

    railway_graph = build_railway_graph(hub_stations, hub_edges)
    plot_railway_graph(railway_graph)



if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("GTFS preparation failed")
        raise