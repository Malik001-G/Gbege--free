import random
from backend.graph_loader import RoadGraph
from backend.heuristics import haversine_distance
from backend.search import breadth_first_search, greedy_best_first_search, astar_search

def main():
    # 1. Load the road graph
    rg = RoadGraph()

    # Heuristic adapter: receives node IDs u and v and returns straight-line distance in meters
    def h(u: int, v: int) -> float:
        coord_u = rg.get_node_coords(u)
        coord_v = rg.get_node_coords(v)
        return haversine_distance(coord_u, coord_v)

    # 2. Pick two random distinct nodes from the network
    all_nodes = list(rg.nodes.keys())
    random.seed(42)  # For reproducible comparison
    start_node = random.choice(all_nodes)
    goal_node = random.choice(all_nodes)

    while goal_node == start_node:
        goal_node = random.choice(all_nodes)

    start_lat, start_lon = rg.get_node_coords(start_node)
    goal_lat, goal_lon = rg.get_node_coords(goal_node)

    print(f"\n--- Testing Route Search ---")
    print(f"Start Node: {start_node} ({start_lat:.4f}, {start_lon:.4f})")
    print(f"Goal Node:  {goal_node} ({goal_lat:.4f}, {goal_lon:.4f})")
    print(f"Direct Haversine distance: {h(start_node, goal_node):.2f} meters\n")

    # 3. Run BFS
    bfs_path, bfs_explored, bfs_stats = breadth_first_search(rg.adjacency, start_node, goal_node)
    print(f"[BFS]     Found path: {len(bfs_path) if bfs_path else 0} nodes | Explored: {bfs_stats['nodes_explored']} | Distance: {bfs_stats['distance_m']:.1f} m | Time: {bfs_stats['time_ms']} ms")

    # 4. Run Greedy Best-First
    greedy_path, greedy_explored, greedy_stats = greedy_best_first_search(rg.adjacency, start_node, goal_node, h)
    print(f"[Greedy]  Found path: {len(greedy_path) if greedy_path else 0} nodes | Explored: {greedy_stats['nodes_explored']} | Distance: {greedy_stats['distance_m']:.1f} m | Time: {greedy_stats['time_ms']} ms")

    # 5. Run A*
    astar_path, astar_explored, astar_stats = astar_search(rg.adjacency, start_node, goal_node, h)
    print(f"[A*]      Found path: {len(astar_path) if astar_path else 0} nodes | Explored: {astar_stats['nodes_explored']} | Distance: {astar_stats['distance_m']:.1f} m | Time: {astar_stats['time_ms']} ms")

if __name__ == "__main__":
    main()