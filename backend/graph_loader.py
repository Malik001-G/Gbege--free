import os
from typing import Dict, List, Tuple
import networkx as nx
import osmnx as ox

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
GRAPH_CACHE_FILE = os.path.join(DATA_DIR, "victoria_island.graphml")

class RoadGraph:
    def __init__(self, cache_file: str = GRAPH_CACHE_FILE):
        self.cache_file = cache_file
        self.adjacency: Dict[int, List[Tuple[int, float]]] = {}
        self.nodes: Dict[int, Tuple[float, float]] = {}
        self._load_and_prepare_graph()

    def _load_and_prepare_graph(self):
        if not os.path.exists(self.cache_file):
            raise FileNotFoundError(f"Missing cache file at {self.cache_file}")

        print(f"[*] Loading cached road graph from {self.cache_file}...")
        ox_graph = ox.load_graphml(self.cache_file)
        self._build_custom_structures(ox_graph)
        print(f"[+] Loaded {len(self.nodes)} nodes and {sum(len(edges) for edges in self.adjacency.values())} directed edges.")

    def _build_custom_structures(self, ox_graph: nx.MultiDiGraph):
        self.adjacency.clear()
        self.nodes.clear()

        for node_id, data in ox_graph.nodes(data=True):
            self.nodes[node_id] = (float(data["y"]), float(data["x"]))
            self.adjacency[node_id] = []

        edge_dict: Dict[Tuple[int, int], float] = {}
        for u, v, data in ox_graph.edges(data=True):
            length = float(data.get("length", 1.0))
            pair = (u, v)
            if pair not in edge_dict or length < edge_dict[pair]:
                edge_dict[pair] = length

        for (u, v), length in edge_dict.items():
            if u in self.adjacency and v in self.nodes:
                self.adjacency[u].append((v, length))

    def snap_to_nearest_node(self, lat: float, lon: float) -> int:
        best_node = None
        min_dist_sq = float("inf")
        for node_id, (n_lat, n_lon) in self.nodes.items():
            dist_sq = (n_lat - lat) ** 2 + (n_lon - lon) ** 2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                best_node = node_id
        if best_node is None:
            raise ValueError("Road network has no nodes.")
        return best_node

    def get_node_coords(self, node_id: int) -> Tuple[float, float]:
        return self.nodes[node_id]