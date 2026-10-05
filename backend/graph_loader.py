import os
from typing import Dict, List, Tuple, Any
import networkx as nx
import osmnx as ox

# Cache file location
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
GRAPH_CACHE_FILE = os.path.join(DATA_DIR, "unilag_akoka.graphml")

# Default study area: University of Lagos & Akoka area, Lagos, Nigeria
DEFAULT_PLACE = "University of Lagos, Akoka, Lagos, Nigeria"


class RoadGraph:
    """
    Manages loading, caching, and querying an OpenStreetMap drivable network.
    Converts NetworkX/OSMnx MultiDiGraph into lightweight structures for our pure search code.
    """

    def __init__(self, place_name: str = DEFAULT_PLACE, cache_file: str = GRAPH_CACHE_FILE):
        self.place_name = place_name
        self.cache_file = cache_file

        # Adjacency list: node_id -> list of (neighbor_id, distance_meters)
        self.adjacency: Dict[int, List[Tuple[int, float]]] = {}
        # Node coordinates: node_id -> (lat, lon)
        self.nodes: Dict[int, Tuple[float, float]] = {}

        self._load_and_prepare_graph()

    def _load_and_prepare_graph(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

        if os.path.exists(self.cache_file):
            print(f"[*] Loading cached road graph from {self.cache_file}...")
            ox_graph = ox.load_graphml(self.cache_file)
        else:
            print(f"[*] Downloading network for '{self.place_name}' from OpenStreetMap...")
            ox_graph = ox.graph_from_place(self.place_name, network_type="drive")

            # Extract the largest strongly connected component using standard NetworkX
            # This ensures any start node can reach any end node on directed roads
            largest_scc_nodes = max(nx.strongly_connected_components(ox_graph), key=len)
            ox_graph = ox_graph.subgraph(largest_scc_nodes).copy()

            print(f"[*] Saving graph cache to {self.cache_file}...")
            ox.save_graphml(ox_graph, self.cache_file)

        # Build pure Python adjacency list and coordinates dictionary
        self._build_custom_structures(ox_graph)
        print(f"[+] Loaded {len(self.nodes)} nodes and {sum(len(edges) for edges in self.adjacency.values())} directed edges.")
        
 
    def _build_custom_structures(self, ox_graph: nx.MultiDiGraph):
        self.adjacency.clear()
        self.nodes.clear()

        # Extract coordinates: node -> (lat, lon)
        for node_id, data in ox_graph.nodes(data=True):
            self.nodes[node_id] = (float(data["y"]), float(data["x"]))  # y is lat, x is lon
            self.adjacency[node_id] = []

        # Extract shortest edge length for multiple parallel edges
        # In MultiDiGraph, (u, v) can have multiple parallel edges; pick min length
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
        """
        Finds the closest graph node ID to the given GPS coordinates
        using Euclidean distance over coordinates (fast enough for local searches).
        """
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