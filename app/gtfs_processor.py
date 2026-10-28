import logging

import pandas as pd

logger = logging.getLogger(__name__)

def filter_irish_rail_data(gtfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    logger.info("Filtering Irish Rail data")

    routes = gtfs["routes"].loc[
        gtfs["routes"]["agency_id"] == "IR"
    ].copy()

    trips = gtfs["trips"].loc[
        gtfs["trips"]["route_id"].isin(routes["route_id"])
    ].copy()

    stop_times = gtfs["stop_times"].loc[
        gtfs["stop_times"]["trip_id"].isin(trips["trip_id"])
    ].copy()

    stops = gtfs["stops"].loc[
        gtfs["stops"]["stop_id"].isin(stop_times["stop_id"])
    ].copy()

    logger.info(
        "Irish Rail subset: %s routes, %s trips, %s stop times, %s stops",
        len(routes),
        len(trips),
        len(stop_times),
        len(stops),
    )
    
    return {
        "stops": stops,
        "routes": routes,
        "trips": trips,
        "stop_times": stop_times,
    }


def build_trip_patterns(trips: pd.DataFrame, stop_times: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Return trips with pattern IDs and a table of distinct stop patterns

    stop_patterns = (
        stop_times
        .sort_values(["trip_id", "stop_sequence"])
        .groupby("trip_id")["stop_id"]
        .agg(tuple)
        .rename("stop_pattern")
    )

    trips_with_patterns = trips.merge(
        stop_patterns,
        on="trip_id",
        how="left",
        validate="one_to_one",
    )

    trips_with_patterns["pattern_id"] = (
        trips_with_patterns
        .groupby(
            ["route_id", "direction_id", "stop_pattern"],
            sort=False,
            dropna=False,
        )
        .ngroup()
    )

    patterns = (
        trips_with_patterns[
            ["pattern_id", "route_id", "direction_id", "stop_pattern"]
        ]
        .drop_duplicates("pattern_id")
        .reset_index(drop=True)
    )

    patterns["origin_stop_id"] = patterns["stop_pattern"].str[0]
    patterns["destination_stop_id"] = patterns["stop_pattern"].str[-1]

    logger.info(
        "Built %s patterns across %s trips",
        len(patterns),
        len(trips_with_patterns),
    )

    return trips_with_patterns, patterns

def build_hub_network(stops: pd.DataFrame, trip_patterns: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Return pattern endpoint stations and connections between them

    hub_stop_ids = set(trip_patterns["origin_stop_id"]) | set(
        trip_patterns["destination_stop_id"]
    )

    hub_stations = (
        stops.loc[stops["stop_id"].isin(hub_stop_ids)]
        .drop_duplicates("stop_id")
        .reset_index(drop=True)
    )

    edges = []

    for pattern in trip_patterns.itertuples(index=False):
        hubs_on_trip = [
            stop_id
            for stop_id in pattern.stop_pattern
            if stop_id in hub_stop_ids
        ]

        edges.extend(
            {
                "route_id": pattern.route_id,
                "origin_stop_id": origin,
                "destination_stop_id": destination,
            }
            for origin, destination in zip(
                hubs_on_trip,
                hubs_on_trip[1:],
            )
        )

    hub_edges = (
        pd.DataFrame(
            edges,
            columns=["route_id", "origin_stop_id", "destination_stop_id"],
        )
        .drop_duplicates()
        .reset_index(drop=True)
    )

    logger.info(
        "Built hub network: %s stations, %s connections",
        len(hub_stations),
        len(hub_edges),
    )

    return hub_stations, hub_edges