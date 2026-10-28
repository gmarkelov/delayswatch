"""This script is building the railway graph from GTFS data for path finder application"""

import logging

from pathlib import Path
import networkx as nx
import pandas as pd
import json

logger = logging.getLogger(__name__)

def build_railway_graph(stops: pd.DataFrame, sections_path: Path) -> nx.Graph:
    """Build station connections from ordered railway sections."""

    logger.info("Building railway graph from %s", sections_path)

    with sections_path.open(encoding="utf-8") as file:
        sections = json.load(file)

    graph = nx.Graph()

    for section_name, station_names in sections.items():
        section_stop_ids = []

        for station_name in station_names:
            matches = stops.loc[stops["stop_name"] == station_name]

            if len(matches) != 1:
                raise ValueError(
                    f"Expected one GTFS stop for {station_name!r}; "
                    f"found {len(matches)}"
                )

            station = matches.iloc[0]
            stop_id = station["stop_id"]

            graph.add_node(
                stop_id,
                name=station["stop_name"],
                latitude=station["stop_lat"],
                longitude=station["stop_lon"],
            )

            section_stop_ids.append(stop_id)

        for origin, destination in zip(
            section_stop_ids,
            section_stop_ids[1:],
        ):
            graph.add_edge(origin, destination)

    logger.info(
        "Built railway graph: %s stations, %s connections",
        graph.number_of_nodes(),
        graph.number_of_edges(),
    )

    return graph