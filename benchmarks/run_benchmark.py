import csv
import os
import random
import statistics
from typing import Dict, List, Tuple
from backend.graph_loader import RoadGraph
from backend.heuristics import haversine_distance
from backend.search import breadth_first_search, greedy_best_first_search, astar_search

def run_benchmarks(num_trips: int = 50, output_csv: str = "benchmarks/results.csv"):
    rg = RoadGraph()
    all_nodes = list(rg.nodes.keys())

    def h(u: int, v: int) -> float:
        return haversine_distance(rg.get_node_coords(u), rg.get_node_coords(v))

    random.seed(42)  # Fixed seed for reproducibility
    results = []

    print(f"[*] Running benchmark across {num_trips} random trips...")

    trip_count = 0
    attempts = 0
    max_attempts = num_trips * 10

    while trip_count < num_trips and attempts < max_attempts:
        attempts += 1
        start = random.choice(all_nodes)
        goal = random.choice(all_nodes)
        if start == goal:
            continue

        # A* reference
        astar_path, _, astar_stats = astar_search(rg.adjacency, start, goal, h)
        if not astar_path:
            continue

        # BFS
        bfs_path, _, bfs_stats = breadth_first_search(rg.adjacency, start, goal)

        # Greedy
        greedy_path, _, greedy_stats = greedy_best_first_search(rg.adjacency, start, goal, h)

        trip_count += 1
        results.append({
            "trip_id": trip_count,
            "start": start,
            "goal": goal,
            "bfs_explored": bfs_stats["nodes_explored"],
            "bfs_dist_m": bfs_stats["distance_m"],
            "bfs_time_ms": bfs_stats["time_ms"],
            "greedy_explored": greedy_stats["nodes_explored"],
            "greedy_dist_m": greedy_stats["distance_m"],
            "greedy_time_ms": greedy_stats["time_ms"],
            "astar_explored": astar_stats["nodes_explored"],
            "astar_dist_m": astar_stats["distance_m"],
            "astar_time_ms": astar_stats["time_ms"],
        })

    # Save to CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    fieldnames = list(results[0].keys())
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"[+] Saved {num_trips} runs to {output_csv}\n")

    # Aggregate summaries
    def avg(lst): return round(statistics.mean(lst), 1)

    bfs_expl = [r["bfs_explored"] for r in results]
    bfs_dist = [r["bfs_dist_m"] for r in results]
    bfs_time = [r["bfs_time_ms"] for r in results]

    greedy_expl = [r["greedy_explored"] for r in results]
    greedy_dist = [r["greedy_dist_m"] for r in results]
    greedy_time = [r["greedy_time_ms"] for r in results]

    astar_expl = [r["astar_explored"] for r in results]
    astar_dist = [r["astar_dist_m"] for r in results]
    astar_time = [r["astar_time_ms"] for r in results]

    # Percentage of trips where algorithm achieved the shortest distance
    bfs_shortest = sum(1 for r in results if r["bfs_dist_m"] <= r["astar_dist_m"] + 1e-2) / num_trips * 100
    greedy_shortest = sum(1 for r in results if r["greedy_dist_m"] <= r["astar_dist_m"] + 1e-2) / num_trips * 100
    astar_shortest = 100.0

    print("=" * 68)
    print(f"{'Metric':<30} | {'BFS':<10} | {'Greedy':<10} | {'A*':<10}")
    print("=" * 68)
    print(f"{'Average nodes explored':<30} | {avg(bfs_expl):<10} | {avg(greedy_expl):<10} | {avg(astar_expl):<10}")
    print(f"{'Average route length (m)':<30} | {avg(bfs_dist):<10} | {avg(greedy_dist):<10} | {avg(astar_dist):<10}")
    print(f"{'Routes that were shortest (%)':<30} | {bfs_shortest:<10.1f} | {greedy_shortest:<10.1f} | {astar_shortest:<10.1f}")
    print(f"{'Average compute time (ms)':<30} | {avg(bfs_time):<10} | {avg(greedy_time):<10} | {avg(astar_time):<10}")
    print("=" * 68)

if __name__ == "__main__":
    run_benchmarks()