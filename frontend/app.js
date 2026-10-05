const map = L.map("map");

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

let startPoint = null;
let endPoint = null;
let currentAlgo = "astar";
let graphBounds = null;

let startMarker = null;
let endMarker = null;
let boundaryLayer = L.layerGroup().addTo(map);
let exploredLayer = L.layerGroup().addTo(map);
let pathLayer = L.layerGroup().addTo(map);

const statusEl = document.getElementById("status");
const statsEl = document.getElementById("stats");
const statAlgo = document.getElementById("stat-algo");
const statExplored = document.getElementById("stat-explored");
const statDist = document.getElementById("stat-dist");
const statTime = document.getElementById("stat-time");
const algoButtons = document.querySelectorAll(".algo-btn");
const resetBtn = document.getElementById("btn-reset");

async function initGraphBounds() {
  try {
    const res = await fetch("http://127.0.0.1:8000/info");
    const data = await res.json();
    graphBounds = data.bounds;

    map.fitBounds(graphBounds, { padding: [40, 40] });

    L.rectangle(graphBounds, {
      color: "#2563eb",
      weight: 2,
      dashArray: "6, 8",
      fillOpacity: 0.05,
    }).addTo(boundaryLayer);

    statusEl.innerText = "Click inside the blue dashed area to set Start.";
  } catch (err) {
    statusEl.innerText = "Backend offline. Run uvicorn on port 8000.";
  }
}

initGraphBounds();

algoButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    algoButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentAlgo = btn.dataset.algo;
    if (startPoint && endPoint) {
      fetchRoute();
    }
  });
});

map.on("click", (e) => {
  const { lat, lng } = e.latlng;

  if (graphBounds) {
    const [[minLat, minLng], [maxLat, maxLng]] = graphBounds;
    if (lat < minLat || lat > maxLat || lng < minLng || lng > maxLng) {
      statusEl.innerText = "Point outside network. Click inside the dashed border.";
      return;
    }
  }

  if (!startPoint) {
    startPoint = { lat, lng };
    startMarker = L.marker([lat, lng], {
      icon: L.icon({
        iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
      }),
    }).addTo(map).bindPopup("Start").openPopup();
    statusEl.innerText = "Start set! Click inside border for Destination.";
  } else if (!endPoint) {
    endPoint = { lat, lng };
    endMarker = L.marker([lat, lng], {
      icon: L.icon({
        iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
      }),
    }).addTo(map).bindPopup("Destination").openPopup();
    statusEl.innerText = "Routing...";
    fetchRoute();
  }
});

async function fetchRoute() {
  clearSearchVisuals();
  statusEl.innerText = `Searching with ${currentAlgo.toUpperCase()}...`;

  try {
    const res = await fetch("http://127.0.0.1:8000/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start: startPoint,
        end: endPoint,
        algorithm: currentAlgo,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Route request failed");
    }

    const data = await res.json();
    renderExploredAndPath(data);
  } catch (err) {
    statusEl.innerText = `Error: ${err.message}`;
  }
}

function renderExploredAndPath(data) {
  const { path, explored, stats } = data;

  explored.forEach((coord) => {
    L.circleMarker(coord, {
      radius: 4,
      fillColor: currentAlgo === "bfs" ? "#3b82f6" : currentAlgo === "greedy" ? "#f59e0b" : "#10b981",
      color: "#ffffff",
      weight: 1,
      opacity: 0.8,
      fillOpacity: 0.6,
    }).addTo(exploredLayer);
  });

  L.polyline(path, {
    color: "#2563eb",
    weight: 5,
    opacity: 0.9,
  }).addTo(pathLayer);

  statsEl.style.display = "block";
  statAlgo.innerText = currentAlgo.toUpperCase();
  statExplored.innerText = stats.nodes_explored;
  statDist.innerText = `${stats.distance_m.toFixed(1)} m`;
  statTime.innerText = `${stats.time_ms} ms`;
  statusEl.innerText = `Route found! Switch algorithms above to compare.`;
}

function clearSearchVisuals() {
  exploredLayer.clearLayers();
  pathLayer.clearLayers();
}

function resetAll() {
  startPoint = null;
  endPoint = null;
  if (startMarker) map.removeLayer(startMarker);
  if (endMarker) map.removeLayer(endMarker);
  clearSearchVisuals();
  statsEl.style.display = "none";
  statusEl.innerText = "Click inside the blue dashed area to set Start.";
}

resetBtn.addEventListener("click", resetAll);