```markdown
# Gbege Free

Route planner that compares BFS, Greedy Best-First, and A* on real Lagos roads. Built as my capstone project for CS50 AI.

"Gbege" is Nigerian Pidgin for hassle or trouble — so the goal here is hassle-free routing.



## What it does

Most map apps only show you the final polyline. This project visually shows how different search algorithms explore road networks to get there:

- Uses drivable road graphs pulled from OpenStreetMap for Victoria Island, Lagos.
- Search algorithms (BFS, Greedy, A*) are implemented entirely from scratch in pure Python using standard library data structures (`heapq`, `deque`) — no third-party pathfinding libraries.
- Renders the explored frontier nodes on an interactive Leaflet map to show how each algorithm handles street networks, one-ways, and bridges.
- Includes an automated benchmark script that runs all three algorithms across 50 identical random trips to measure nodes explored, route distance, and execution time.

## Tech Stack

- **Search Core:** Pure Python (`collections.deque`, `heapq`)
- **Map Data:** OpenStreetMap via `osmnx` (cached to `.graphml`)
- **Backend API:** FastAPI, Uvicorn
- **Frontend:** Vanilla JavaScript, Leaflet.js
- **Testing & Benchmarks:** `pytest`, Python `csv` module

## Search Formulation

- **State:** Road intersection node IDs from OpenStreetMap.
- **Actions:** Directed road segments leaving the current junction.
- **Transition:** The junction node at the end of the road segment.
- **Path Cost ($g(n)$):** Physical road length in meters.
- **Heuristic ($h(n)$):** Straight-line Haversine distance from the current junction to the destination. It is admissible because straight-line distance is physically the shortest path between two points on Earth — no drivable road can ever be shorter than a straight line.

## Benchmark Results (50 Trips on Victoria Island)

All three algorithms were evaluated over the same 50 random start/end pairs:

| Metric | BFS | Greedy Best-First | A* |
| :--- | :---: | :---: | :---: |
| **Avg. Nodes Explored** | 349.5 | **41.3** | 110.1 |
| **Avg. Route Length (m)** | 3,142.1 m | 3,454.4 m | **3,006.3 m** |
| **Shortest Route Found (%)** | 52.0% | 38.0% | **100.0%** |
| **Avg. Compute Time (ms)** | 0.23 ms | **0.08 ms** | 0.19 ms |

### Analysis

1. **A* matches optimal distance with 68% fewer nodes than BFS:** BFS expands blindly in all directions, checking roughly 350 nodes per trip. By using the Haversine heuristic to bias the search toward the destination, A* cuts exploration down to 110 nodes while guaranteeing the shortest path every time.
2. **Greedy trades route quality for speed:** Greedy explores the fewest nodes (41.3) and runs the fastest (0.08 ms). However, because it only prioritizes $h(n)$ and ignores accumulated road distance ($g(n)$), it frequently gets trapped in detours — only finding the shortest path 38% of the time and producing routes that are on average ~450 meters (15%) longer.
3. **BFS finds fewest segments, not shortest distance:** BFS optimizes for the fewest graph hops (road segments), not metric length. Because street segment lengths vary widely in real cities, BFS found the shortest metric path in only 52% of runs.

## Project Structure

```text
gbege-free/
├── backend/
│   ├── __init__.py
│   ├── api.py              # FastAPI endpoints (/route, /info)
│   ├── graph_loader.py     # Graph loading, SCC extraction, and caching
│   ├── heuristics.py       # Haversine distance heuristic
│   ├── search.py           # Custom BFS, Greedy, and A* implementations
│   └── tests/
│       ├── __init__.py
│       └── test_search.py  # Unit tests for algorithm correctness
├── frontend/
│   ├── index.html          # Interactive Leaflet map interface
│   └── app.js              # Map event handling and route visualization
├── benchmarks/
│   ├── run_benchmark.py    # 50-trip automated evaluation script
│   └── results.csv         # Raw CSV output from the benchmark run
├── data/
│   └── victoria_island.graphml  # Cached road network
├── docs/
│   └── demo.png            # Interface screenshot
├── requirements.txt
└── README.md

```

## Setup & Running Locally

### 1. Clone the repository and install requirements

```bash
git clone [https://github.com/](https://github.com/)<your-username>/gbege-free.git
cd gbege-free

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

### 2. Run the unit tests

```bash
python -m pytest backend/tests/test_search.py

```

### 3. Start the backend API

```bash
uvicorn backend.api:app --reload --port 8000

```

### 4. Open the map interface

Open `frontend/index.html` directly in your browser (or use VS Code Live Server / `python -m http.server 3000` from the `frontend/` folder).

* Click inside the blue boundary to set a **Start** point (green pin).
* Click a second location to set a **Destination** point (red pin).
* Use the toggle buttons to switch between **BFS**, **Greedy**, and **A*** to inspect the explored nodes and performance metrics.

### 5. Re-run benchmarks

To re-run the 50-trip benchmark and generate a fresh `benchmarks/results.csv`:

```bash
python -m benchmarks.run_benchmark

```

```

```