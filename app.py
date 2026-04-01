import streamlit as st
import networkx as nx
import folium
import copy
import math
import heapq
from collections import deque

st.set_page_config(page_title="Route Optimizer", layout="centered")
st.title("🚦 Smart Traffic Route Optimization (Nagpur)")

# 📍 Locations
locations = {
    "Sitabuldi": (21.1458, 79.0882),
    "Dharampeth": (21.1405, 79.0700),
    "Ramdaspeth": (21.1360, 79.0820),
    "Trimurti Nagar": (21.1200, 79.0600),
    "Manish Nagar": (21.1100, 79.0950),
    "Medical Square": (21.1550, 79.1000),
    "Airport": (21.0922, 79.0473),
    "Wardha Road": (21.1205, 79.0850)
}

# 🔗 Graph
base_G = nx.Graph()
edges = [
    ("Sitabuldi","Dharampeth",4),
    ("Sitabuldi","Ramdaspeth",2),
    ("Dharampeth","Ramdaspeth",1),
    ("Dharampeth","Medical Square",5),
    ("Ramdaspeth","Manish Nagar",7),
    ("Medical Square","Manish Nagar",3),
    ("Trimurti Nagar","Dharampeth",6),
    ("Manish Nagar","Airport",5),
    ("Ramdaspeth","Wardha Road",4),
    ("Wardha Road","Airport",3)
]
base_G.add_weighted_edges_from(edges)

# 🚦 Traffic (ONLY Low & High)
traffic_data = {
    ("Sitabuldi","Dharampeth"): "High",
    ("Sitabuldi","Ramdaspeth"): "Low",
    ("Dharampeth","Ramdaspeth"): "Low",
    ("Dharampeth","Medical Square"): "High",
    ("Ramdaspeth","Manish Nagar"): "Low",
    ("Medical Square","Manish Nagar"): "High",
    ("Trimurti Nagar","Dharampeth"): "Low",
    ("Manish Nagar","Airport"): "Low",
    ("Ramdaspeth","Wardha Road"): "High",
    ("Wardha Road","Airport"): "Low"
}

nodes = list(locations.keys())

# 🎛️ UI
source = st.selectbox("📍 Select Source", nodes)
destination = st.selectbox("🏁 Select Destination", nodes)
traffic_level = st.selectbox("🚦 Traffic Mode", ["Low", "Medium", "High"])
traffic_sensitivity = st.slider("🌡️ Traffic Sensitivity", 0.5, 2.0, 1.0, step=0.1)
algorithm = st.selectbox("🧠 Algorithm", ["Dijkstra", "A*", "DFS", "BFS", "AO*"])
show_graph = st.checkbox("Show road weights and traffic")

# ⚙️ Functions
def get_mode_factor(mode):
    return {"Low": 0.8, "Medium": 1.0, "High": 1.6}[mode]

def get_road_penalty(traffic):
    return {"Low": 0.0, "Medium": 1.0, "High": 2.0}[traffic]

def build_weighted_graph(traffic_level, sensitivity):
    G = copy.deepcopy(base_G)
    for u, v, d in G.edges(data=True):
        base = d["weight"]
        traffic = traffic_data.get((u, v)) or traffic_data.get((v, u)) or "Low"
        penalty = get_road_penalty(traffic)
        factor = get_mode_factor(traffic_level)
        d["weight"] = base + base * penalty * factor * sensitivity
    return G

def heuristic(n1, n2):
    x1, y1 = locations[n1]
    x2, y2 = locations[n2]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def route_cost(G, path):
    return sum(G[u][v]["weight"] for u, v in zip(path, path[1:]))

def bfs_search(G, source, destination):
    visited = {source}
    queue = deque([[source]])
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == destination:
            return path
        neighbors = sorted(
            G.neighbors(node),
            key=lambda n: (G[node][n]["weight"], heuristic(n, destination))
        )
        for nbr in neighbors:
            if nbr not in visited:
                visited.add(nbr)
                queue.append(path + [nbr])
    raise nx.NetworkXNoPath(f"No path found from {source} to {destination}")

def dfs_search(G, source, destination):
    visited = set()
    stack = [[source]]
    while stack:
        path = stack.pop()
        node = path[-1]
        if node == destination:
            return path
        if node in visited:
            continue
        visited.add(node)
        neighbors = sorted(
            G.neighbors(node),
            key=lambda n: (G[node][n]["weight"], heuristic(n, destination))
        )
        for nbr in reversed(neighbors):
            if nbr not in visited:
                stack.append(path + [nbr])
    raise nx.NetworkXNoPath(f"No path found from {source} to {destination}")

def ao_star_path(G, source, destination):
    queue = [(heuristic(source, destination), 0.0, source, [source])]
    best_cost = {source: 0.0}
    while queue:
        _, cost_so_far, node, path = heapq.heappop(queue)
        if node == destination:
            return path
        if cost_so_far > best_cost.get(node, float("inf")):
            continue
        for nbr in G.neighbors(node):
            if nbr in path:
                continue
            new_cost = cost_so_far + G[node][nbr]["weight"]
            if new_cost < best_cost.get(nbr, float("inf")):
                best_cost[nbr] = new_cost
                heapq.heappush(
                    queue,
                    (new_cost + heuristic(nbr, destination), new_cost, nbr, path + [nbr])
                )
    raise nx.NetworkXNoPath(f"No path found from {source} to {destination}")

def solve_route(G, source, destination, algorithm):
    if algorithm == "Dijkstra":
        path = nx.shortest_path(G, source, destination, weight='weight')
        distance = nx.shortest_path_length(G, source, destination, weight='weight')
        return path, distance, []
    if algorithm == "A*":
        path = nx.astar_path(G, source, destination, heuristic=heuristic, weight='weight')
        distance = nx.astar_path_length(G, source, destination, heuristic=heuristic, weight='weight')
        return path, distance, []
    if algorithm == "BFS":
        path = bfs_search(G, source, destination)
        return path, route_cost(G, path), []
    if algorithm == "DFS":
        path = dfs_search(G, source, destination)
        return path, route_cost(G, path), []
    if algorithm == "AO*":
        path = ao_star_path(G, source, destination)
        return path, route_cost(G, path), []
    raise ValueError(f"Unsupported algorithm: {algorithm}")

# 🚀 Run
if st.button("🚀 Find Optimal Route"):

    if source == destination:
        st.warning("Source and Destination cannot be same!")
    else:
        try:
            G = build_weighted_graph(traffic_level, traffic_sensitivity)

            path, distance, alternatives = solve_route(G, source, destination, algorithm)

            st.success(f"✅ Best Route ({algorithm}): {' → '.join(path)}")
            st.info(f"📏 Estimated Distance: {round(distance,2)}")
            st.info(f"🛣️ Traffic mode: {traffic_level}, sensitivity: {traffic_sensitivity}")

            if show_graph:
                st.write("### 🧠 Graph edge weights + traffic")
                graph_rows = []
                for u, v, d in G.edges(data=True):
                    traffic = traffic_data.get((u, v)) or traffic_data.get((v, u)) or "Low"
                    graph_rows.append({
                        "road": f"{u} ↔ {v}",
                        "weight": round(d['weight'], 2),
                        "traffic": traffic
                    })
                st.table(graph_rows)

            # 🗺️ Map
            route_coords = [locations[node] for node in path]
            m = folium.Map(location=[21.1458, 79.0882], zoom_start=12)
            m.fit_bounds(route_coords)

            # Markers
            for place, coord in locations.items():
                color = "green" if place == source else "red" if place == destination else "blue"
                folium.Marker(coord, popup=place, icon=folium.Icon(color=color)).add_to(m)

            # Roads
            for u, v, d in G.edges(data=True):
                coords = [locations[u], locations[v]]
                traffic = traffic_data.get((u, v)) or traffic_data.get((v, u)) or "Low"

                color = "green" if traffic == "Low" else "red"
                folium.PolyLine(coords, color=color, weight=3).add_to(m)

            # Best route
            folium.PolyLine(route_coords, color="blue", weight=6).add_to(m)

            st.components.v1.html(m._repr_html_(), height=600)

        except Exception as e:
            st.error(f"Error: {e}")