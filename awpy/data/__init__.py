"""Provides data such as radar images and navigation meshes."""
import json
import os
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy.spatial import distance

from awpy.types import Area, AreaMatrix, MapData, PlaceMatrix
from awpy.utils import transform_csv_to_json

PATH = os.path.join(os.path.dirname(__file__), "")

NAV_CSV = pd.read_csv(PATH + "nav/nav_info.csv")
NAV_CSV.areaName = NAV_CSV.areaName.fillna("")


NAV: dict[str, dict[int, Area]] = transform_csv_to_json(NAV_CSV)


def create_nav_graphs(
    nav: dict[str, dict[int, Area]], data_path: str
) -> dict[str, nx.DiGraph]:
    """Function to create a dict of DiGraphs from dict of areas and edge_list file.

    Args:
        nav (dict): Dictionary containing information about each area of each map
        data_path (str): Path to the awpy.data folder containing navigation and map data

    Returns:
        A dictionary mapping each map (str) to an nx.DiGraph of its traversible areas
    """
    nav_graphs: dict[str, nx.DiGraph] = {}
    for m in nav:
        map_graph = nx.DiGraph()
        for a in nav[m]:
            r = nav[m][a]
            map_graph.add_nodes_from(
                [
                    (
                        a,
                        {
                            "mapName": m,
                            "areaID": a,
                            "areaName": r["areaName"],
                            "northWestX": r["northWestX"],
                            "northWestY": r["northWestY"],
                            "northWestZ": r["northWestZ"],
                            "southEastX": r["southEastX"],
                            "southEastY": r["southEastY"],
                            "southEastZ": r["southEastZ"],
                            "center": [
                                (r["northWestX"] + r["southEastX"]) / 2,
                                (r["northWestY"] + r["southEastY"]) / 2,
                                (r["northWestZ"] + r["southEastZ"]) / 2,
                            ],
                            "size": np.sqrt(
                                (r["northWestX"] - r["southEastX"]) ** 2
                                + (r["northWestY"] - r["southEastY"]) ** 2
                                + (r["northWestZ"] - r["southEastZ"]) ** 2
                            ),
                        },
                    ),
                ]
            )
        with open(data_path + "nav/" + m + ".txt", encoding="utf8") as edge_list:
            edge_list_lines = edge_list.readlines()
        for line in edge_list_lines:
            areas = line.strip().split(",")
            map_graph.add_edge(
                int(areas[0]),
                int(areas[1]),
                weight=distance.euclidean(
                    map_graph.nodes()[int(areas[0])]["center"],
                    map_graph.nodes()[int(areas[1])]["center"],
                ),
            )
        nav_graphs[m] = map_graph
    return nav_graphs


NAV_GRAPHS = create_nav_graphs(NAV, PATH)

# Open map data
with open(Path(PATH + "map/map_data.json"), encoding="utf8") as f:
    MAP_DATA: dict[str, MapData] = json.load(f)

PLACE_DIST_MATRIX: dict[str, PlaceMatrix] = {}
AREA_DIST_MATRIX: dict[str, AreaMatrix] = {}
for file in os.listdir(PATH + "nav/"):
    if file.startswith("place_distance_matrix"):
        this_map_name = "_".join(file.split(".")[0].split("_")[-2:])
        with open(Path(PATH + "nav/" + file), encoding="utf8") as f:
            PLACE_DIST_MATRIX[this_map_name] = json.load(f)
    elif file.startswith("area_distance_matrix"):
        this_map_name = "_".join(file.split(".")[0].split("_")[-2:])
        with open(Path(PATH + "nav/" + file), encoding="utf8") as f:
            AREA_DIST_MATRIX[this_map_name] = json.load(f)