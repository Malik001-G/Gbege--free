from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal, Tuple

from backend.graph_loader import RoadGraph
from backend.heuristics import haversine_distance
from backend.search import breadth_first_search, greedy_best_first_search, astar_search

app = FastAPI(title="Gbege Free API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

road_graph = RoadGraph()

class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)

class RouteRequest(BaseModel):
    start: Coordinate
    end: Coordinate
    algorithm: Literal["bfs", "greedy", "astar"] = "astar"

class RouteStats(BaseModel):
    nodes_explored: int
    distance_m: float
    time_ms: float

class RouteResponse(BaseModel):
    path: List[Tuple[float, float]]
    explored: List[Tuple[float, float]]
    stats: RouteStats

@app.get("/info")
def get_graph_info():
    lats = [coord[0] for coord in road_graph.nodes.values()]
    lons = [coord[1] for coord in road_graph.nodes.values()]
    return {
        "bounds": [
            [min(lats), min(lons)],
            [max(lats), max(lons)]
        ],
        "total_nodes": len(road_graph.nodes),
        "total_edges": sum(len(e) for e in road_graph.adjacency.values())
    }

@app.post("/route", response_model=RouteResponse)
def compute_route(req: RouteRequest):
    try:
        start_node = road_graph.snap_to_nearest_node(req.start.lat, req.start.lng)
        goal_node = road_graph.snap_to_nearest_node(req.end.lat, req.end.lng)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Snap failed: {str(e)}")

    if start_node == goal_node:
        raise HTTPException(status_code=400, detail="Start and destination points are too close.")

    def h(u: int, v: int) -> float:
        return haversine_distance(road_graph.get_node_coords(u), road_graph.get_node_coords(v))

    if req.algorithm == "bfs":
        node_path, explored_nodes, stats = breadth_first_search(road_graph.adjacency, start_node, goal_node)
    elif req.algorithm == "greedy":
        node_path, explored_nodes, stats = greedy_best_first_search(road_graph.adjacency, start_node, goal_node, h)
    elif req.algorithm == "astar":
        node_path, explored_nodes, stats = astar_search(road_graph.adjacency, start_node, goal_node, h)
    else:
        raise HTTPException(status_code=400, detail="Unknown algorithm")

    if not node_path:
        raise HTTPException(status_code=404, detail="No route found between these points.")

    return RouteResponse(
        path=[road_graph.get_node_coords(nid) for nid in node_path],
        explored=[road_graph.get_node_coords(nid) for nid in explored_nodes],
        stats=RouteStats(**stats)
    )