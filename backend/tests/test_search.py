import math
import pytest
from backend.search import breadth_first_search, greedy_best_first_search, astar_search

def test_algorithm_behavior():
    # Setup test graph:
    # Path 1: A -> D (1 segment, length 100m)
    # Path 2: A -> B -> C -> D (3 segments, 10m each = 30m)
    coords = {
        "A": (0.0, 0.0),
        "B": (0.0, 1.0),
        "C": (0.0, 2.0),
        "D": (0.0, 3.0)
    }
    graph = {
        "A": [("D", 100.0), ("B", 10.0)],
        "B": [("C", 10.0)],
        "C": [("D", 10.0)],
        "D": []
    }

    def simple_h(u, v):
        return math.hypot(coords[u][0] - coords[v][0], coords[u][1] - coords[v][1]) * 10.0

    bfs_path, _, bfs_stats = breadth_first_search(graph, "A", "D")
    astar_path, _, astar_stats = astar_search(graph, "A", "D", simple_h)
    greedy_path, _, greedy_stats = greedy_best_first_search(graph, "A", "D", simple_h)

    # 1. BFS optimizes for segments, returning 100m
    assert bfs_path == ["A", "D"]
    assert bfs_stats["distance_m"] == 100.0

    # 2. A* finds the optimal path by distance
    assert astar_path == ["A", "B", "C", "D"]
    assert astar_stats["distance_m"] == 30.0

    # 3. Greedy finds a valid path to D
    assert greedy_path is not None and greedy_path[-1] == "D"