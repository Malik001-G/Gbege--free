import os
import networkx as nx
import osmnx as ox

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
GRAPH_CACHE_FILE = os.path.join(DATA_DIR, "lagos_mainland.graphml")

# Yaba central coordinates (Commercial Ave / Sabo), 1800m radius
MAINLAND_CENTER = (6.5095, 3.3790)
MAINLAND_RADIUS_METERS = 1800

# List of public mirrors to try in order
OVERPASS_MIRRORS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Configure OSMnx settings across both v1 and v2 syntax
    ox.settings.requests_timeout = 180
    ox.settings.max_query_area_size = 2500000000

    downloaded = False
    for endpoint in OVERPASS_MIRRORS:
        print(f"[*] Attempting download using mirror: {endpoint} ...")
        # Set both attributes to ensure compatibility
        try:
            ox.settings.overpass_url = endpoint
        except AttributeError:
            pass
        try:
            ox.settings.overpass_endpoint = endpoint
        except AttributeError:
            pass

        try:
            G = ox.graph_from_point(
                MAINLAND_CENTER,
                dist=MAINLAND_RADIUS_METERS,
                network_type="drive"
            )
            downloaded = True
            break
        except Exception as e:
            print(f"[-] Mirror {endpoint} failed: {e}")

    if not downloaded:
        print("[!] All online mirrors failed or timed out.")
        return

    # Extract largest strongly connected component
    print("[*] Extracting largest strongly connected component...")
    largest_scc = max(nx.strongly_connected_components(G), key=len)
    clean_graph = G.subgraph(largest_scc).copy()

    # Save cache file
    print(f"[*] Saving graph to {GRAPH_CACHE_FILE}...")
    ox.save_graphml(clean_graph, GRAPH_CACHE_FILE)
    print(f"[+] Done! Downloaded {len(clean_graph.nodes)} nodes and {len(clean_graph.edges)} edges.")

if __name__ == "__main__":
    main()