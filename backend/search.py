from collections import deque
import heapq
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

class Node:
    """Search node representing state, parent link, and path cost g(n)."""
    def __init__(self, state: Any, parent: Optional["Node"] = None, cost: float = 0.0):
        self.state = state
        self.parent = parent
        self.cost = cost

    def __lt__(self, other: "Node") -> bool:
        return self.cost < other.cost

def reconstruct_path(node: Node) -> List[Any]:
    path = []
    curr: Optional[Node] = node
    while curr is not None:
        path.append(curr.state)
        curr = curr.parent
    path.reverse()
    return path

def breadth_first_search(
    graph: Dict[Any, List[Tuple[Any, float]]],
    start: Any,
    goal: Any
) -> Tuple[Optional[List[Any]], List[Any], Dict[str, Any]]:
    """BFS: explores fewest segments (hops) using FIFO queue."""
    t0 = time.perf_counter()
    frontier = deque([Node(state=start, parent=None, cost=0.0)])
    frontier_states = {start}
    explored: Set[Any] = set()
    explored_order: List[Any] = []

    while frontier:
        node = frontier.popleft()
        frontier_states.remove(node.state)
        explored.add(node.state)
        explored_order.append(node.state)

        if node.state == goal:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            return reconstruct_path(node), explored_order, {
                "nodes_explored": len(explored),
                "distance_m": node.cost,
                "time_ms": round(elapsed_ms, 2)
            }

        for neighbor, edge_cost in graph.get(node.state, []):
            if neighbor not in explored and neighbor not in frontier_states:
                child = Node(state=neighbor, parent=node, cost=node.cost + edge_cost)
                frontier.append(child)
                frontier_states.add(neighbor)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return None, explored_order, {
        "nodes_explored": len(explored),
        "distance_m": 0.0,
        "time_ms": round(elapsed_ms, 2)
    }

def greedy_best_first_search(
    graph: Dict[Any, List[Tuple[Any, float]]],
    start: Any,
    goal: Any,
    heuristic: Callable[[Any, Any], float]
) -> Tuple[Optional[List[Any]], List[Any], Dict[str, Any]]:
    """Greedy Best-First: frontier priority solely ordered by h(n)."""
    t0 = time.perf_counter()
    counter = 0
    start_node = Node(state=start, parent=None, cost=0.0)
    frontier = [(heuristic(start, goal), counter, start_node)]
    frontier_states = {start}
    explored: Set[Any] = set()
    explored_order: List[Any] = []

    while frontier:
        _, _, node = heapq.heappop(frontier)
        if node.state in frontier_states:
            frontier_states.remove(node.state)

        explored.add(node.state)
        explored_order.append(node.state)

        if node.state == goal:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            return reconstruct_path(node), explored_order, {
                "nodes_explored": len(explored),
                "distance_m": node.cost,
                "time_ms": round(elapsed_ms, 2)
            }

        for neighbor, edge_cost in graph.get(node.state, []):
            if neighbor not in explored and neighbor not in frontier_states:
                counter += 1
                child = Node(state=neighbor, parent=node, cost=node.cost + edge_cost)
                heapq.heappush(frontier, (heuristic(neighbor, goal), counter, child))
                frontier_states.add(neighbor)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return None, explored_order, {
        "nodes_explored": len(explored),
        "distance_m": 0.0,
        "time_ms": round(elapsed_ms, 2)
    }

def astar_search(
    graph: Dict[Any, List[Tuple[Any, float]]],
    start: Any,
    goal: Any,
    heuristic: Callable[[Any, Any], float]
) -> Tuple[Optional[List[Any]], List[Any], Dict[str, Any]]:
    """A* Search: frontier priority ordered by f(n) = g(n) + h(n)."""
    t0 = time.perf_counter()
    counter = 0
    start_node = Node(state=start, parent=None, cost=0.0)
    frontier = [(heuristic(start, goal), counter, start_node)]
    best_g: Dict[Any, float] = {start: 0.0}
    explored: Set[Any] = set()
    explored_order: List[Any] = []

    while frontier:
        f_cost, _, node = heapq.heappop(frontier)

        if node.state in explored:
            continue

        explored.add(node.state)
        explored_order.append(node.state)

        if node.state == goal:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            return reconstruct_path(node), explored_order, {
                "nodes_explored": len(explored),
                "distance_m": node.cost,
                "time_ms": round(elapsed_ms, 2)
            }

        for neighbor, edge_cost in graph.get(node.state, []):
            new_g = node.cost + edge_cost
            if neighbor not in best_g or new_g < best_g[neighbor]:
                best_g[neighbor] = new_g
                counter += 1
                child = Node(state=neighbor, parent=node, cost=new_g)
                f_child = new_g + heuristic(neighbor, goal)
                heapq.heappush(frontier, (f_child, counter, child))

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return None, explored_order, {
        "nodes_explored": len(explored),
        "distance_m": 0.0,
        "time_ms": round(elapsed_ms, 2)
    }