import streamlit as st
import networkx as nx
import folium
import copy
import math
import heapq
import random
from collections import deque
from datetime import datetime
import requests
import json
from pathlib import Path

st.set_page_config(page_title="Route Optimizer", layout="wide")
st.title("🚦 Smart Traffic Route Optimization (Nagpur)")

# File-based persistence for custom locations
CUSTOM_LOCATIONS_FILE = Path("custom_locations.json")

def load_custom_locations():
    if CUSTOM_LOCATIONS_FILE.exists():
        try:
            with open(CUSTOM_LOCATIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"Could not load custom locations: {e}")
    return {}


def save_custom_locations(custom):
    try:
        with open(CUSTOM_LOCATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(custom, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Could not save custom locations: {e}")

# Initialize session state for persistent custom locations
if "custom_locations" not in st.session_state:
    st.session_state.custom_locations = load_custom_locations()

# 📍 EXPANDED Locations (Demerit Fix #2: More locations for scalability)
locations = {
    "Sitabuldi": (21.1458, 79.0882),
    "Dharampeth": (21.1405, 79.0700),
    "Ramdaspeth": (21.1360, 79.0820),
    "Trimurti Nagar": (21.1200, 79.0600),
    "Manish Nagar": (21.1100, 79.0950),
    "Medical Square": (21.1550, 79.1000),
    "Airport": (21.0922, 79.0473),
    "Wardha Road": (21.1205, 79.0850),
    "Mehta Bridge": (21.1480, 79.0750),
    "Laxmi Nagar": (21.1320, 79.1050),
    "High Court": (21.1480, 79.0900),
    "Imambada": (21.1250, 79.0800),
    "Civil Lines": (21.1150, 79.0700),
    "Seminary Hills": (21.1600, 79.1100),
    "Ravi Nagar": (21.1080, 79.0850),
    "Sadar Bazar": (21.1380, 79.0780)
}

# Merge with custom locations from session state
# Convert list to tuple for coordinate operations
for key, val in st.session_state.custom_locations.items():
    if isinstance(val, list):
        st.session_state.custom_locations[key] = tuple(val)
locations.update(st.session_state.custom_locations)

# 🔗 Graph (Expanded for scalability)
base_G = nx.Graph()
edges = [
    ("Sitabuldi","Dharampeth",4),
    ("Sitabuldi","Ramdaspeth",2),
    ("Sitabuldi","Medical Square",3),
    ("Sitabuldi","High Court",1.5),
    ("Dharampeth","Ramdaspeth",1),
    ("Dharampeth","Medical Square",5),
    ("Dharampeth","Mehta Bridge",2),
    ("Dharampeth","Imambada",3),
    ("Ramdaspeth","Manish Nagar",7),
    ("Ramdaspeth","Wardha Road",4),
    ("Ramdaspeth","Civil Lines",3),
    ("Medical Square","Manish Nagar",3),
    ("Medical Square","Seminary Hills",4),
    ("Medical Square","High Court",2),
    ("Trimurti Nagar","Dharampeth",6),
    ("Trimurti Nagar","Imambada",4),
    ("Manish Nagar","Airport",5),
    ("Manish Nagar","Laxmi Nagar",2),
    ("Wardha Road","Airport",3),
    ("Wardha Road","Ravi Nagar",2),
    ("High Court","Seminary Hills",1),
    ("Mehta Bridge","Laxmi Nagar",3),
    ("Imambada","Civil Lines",2),
    ("Laxmi Nagar","Ravi Nagar",4),
    ("Civil Lines","Sadar Bazar",2),
    ("Sadar Bazar","Seminary Hills",5)
]
base_G.add_weighted_edges_from(edges)

# 🚦 Traffic (Dynamic - Demerit Fix #1: Real-time traffic simulation)
initial_traffic_data = {
    ("Sitabuldi","Dharampeth"): "High",
    ("Sitabuldi","Ramdaspeth"): "Low",
    ("Sitabuldi","Medical Square"): "Low",
    ("Sitabuldi","High Court"): "High",
    ("Dharampeth","Ramdaspeth"): "Low",
    ("Dharampeth","Medical Square"): "High",
    ("Dharampeth","Mehta Bridge"): "Medium",
    ("Dharampeth","Imambada"): "Low",
    ("Ramdaspeth","Manish Nagar"): "Low",
    ("Ramdaspeth","Wardha Road"): "High",
    ("Ramdaspeth","Civil Lines"): "Medium",
    ("Medical Square","Manish Nagar"): "High",
    ("Medical Square","Seminary Hills"): "Low",
    ("Medical Square","High Court"): "Medium",
    ("Trimurti Nagar","Dharampeth"): "Low",
    ("Trimurti Nagar","Imambada"): "High",
    ("Manish Nagar","Airport"): "Low",
    ("Manish Nagar","Laxmi Nagar"): "Medium",
    ("Wardha Road","Airport"): "Low",
    ("Wardha Road","Ravi Nagar"): "High",
    ("High Court","Seminary Hills"): "Low",
    ("Mehta Bridge","Laxmi Nagar"): "Medium",
    ("Imambada","Civil Lines"): "High",
    ("Laxmi Nagar","Ravi Nagar"): "Low",
    ("Civil Lines","Sadar Bazar"): "Medium",
    ("Sadar Bazar","Seminary Hills"): "High"
}
traffic_data = initial_traffic_data.copy()

nodes = list(locations.keys())

# 🎛️ Sidebar Controls
st.sidebar.header("⚙️ Configuration")

# GPS Input (Demerit Fix #4: Real GPS integration simulation)
st.sidebar.subheader("📍 Custom Coordinates")
use_custom_coords = st.sidebar.checkbox("Add custom location with GPS coordinates", value=False)
if use_custom_coords:
    custom_name = st.sidebar.text_input("Location Name", "Custom Location")
    custom_lat = st.sidebar.number_input("Latitude", value=21.14, format="%.4f")
    custom_lon = st.sidebar.number_input("Longitude", value=79.09, format="%.4f")
    if st.sidebar.button("➕ Add Location"):
        # Store in session state for persistence
        st.session_state.custom_locations[custom_name] = [custom_lat, custom_lon]
        save_custom_locations(st.session_state.custom_locations)
        st.sidebar.success(f"✅ Added {custom_name}")
        # Rerun to update locations
        st.rerun()

# Display added custom locations
if st.session_state.custom_locations:
    st.sidebar.subheader("✨ Your Custom Locations")
    for loc_name, coords in st.session_state.custom_locations.items():
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.caption(f"📍 {loc_name}: ({coords[0]:.4f}, {coords[1]:.4f})")
        with col2:
            if st.button("🗑️", key=f"delete_{loc_name}"):
                del st.session_state.custom_locations[loc_name]
                save_custom_locations(st.session_state.custom_locations)
                st.rerun()

# Real-time Traffic Simulator (Demerit Fix #1)
st.sidebar.subheader("🚦 Live Traffic Simulator")
if st.sidebar.button("🔄 Update Traffic (Simulate Live Data)"):
    for edge in traffic_data.keys():
        traffic_data[edge] = random.choice(["Low", "Medium", "High"])
    st.sidebar.success("✅ Traffic updated at " + datetime.now().strftime("%H:%M:%S"))

show_traffic_update = st.sidebar.checkbox("Show last update time", value=True)
if show_traffic_update:
    st.sidebar.info(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Main UI
col1, col2 = st.columns(2)

with col1:
    source = st.selectbox("📍 Select Source", nodes)
    traffic_level = st.selectbox("🚦 Traffic Mode", ["Low", "Medium", "High"])

with col2:
    destination = st.selectbox("🏁 Select Destination", nodes)
    algorithm = st.selectbox("🧠 Algorithm", [
        "Dijkstra (Optimal)",
        "A* (Fast Optimal)", 
        "Greedy Best-First (Weight-Aware)",
        "AO* (Advanced)"
    ])

traffic_sensitivity = st.slider("🌡️ Traffic Sensitivity", 0.5, 2.0, 1.0, step=0.1)
show_graph = st.checkbox("Show road weights and traffic details")

# ⚙️ Functions
def get_mode_factor(mode):
    return {"Low": 0.8, "Medium": 1.0, "High": 1.6}[mode]

def get_road_penalty(traffic):
    return {"Low": 0.0, "Medium": 1.0, "High": 2.0}[traffic]

def build_weighted_graph(traffic_level, sensitivity):
    G = copy.deepcopy(base_G)

    # Add custom nodes (from session state) and connect them to nearest pre-defined nodes.
    for custom_name, coord in st.session_state.custom_locations.items():
        if custom_name not in G:
            G.add_node(custom_name)
        # connect to closest 2 existing nodes for connectivity
        existing_nodes = [n for n in locations.keys() if n != custom_name]
        if existing_nodes:
            neighbours = sorted(
                [(heuristic(custom_name, n), n) for n in existing_nodes],
                key=lambda x: x[0]
            )[:2]
            for dist, neighbour in neighbours:
                if not G.has_edge(custom_name, neighbour):
                    G.add_edge(custom_name, neighbour, weight=dist)

    # Adjust traffic data based on traffic_level
    adjusted_traffic_data = traffic_data.copy()
    if traffic_level == "Low":
        # In low traffic mode, make some roads appear less congested
        for edge in adjusted_traffic_data:
            if adjusted_traffic_data[edge] == "High":
                adjusted_traffic_data[edge] = "Medium"  # Reduce high traffic
    elif traffic_level == "High":
        # In high traffic mode, make some roads appear more congested
        for edge in adjusted_traffic_data:
            if adjusted_traffic_data[edge] == "Low":
                adjusted_traffic_data[edge] = "Medium"  # Increase low traffic

    for u, v, d in G.edges(data=True):
        base = d.get("weight", 1.0)
        traffic = adjusted_traffic_data.get((u, v)) or adjusted_traffic_data.get((v, u)) or "Low"
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

def greedy_best_first_search(G, source, destination):
    """Greedy Best-First Search: Demerit Fix #5 - Weight-aware and heuristic-guided"""
    visited = set()
    heap = [(heuristic(source, destination), 0.0, source, [source])]
    
    while heap:
        _, cost_so_far, node, path = heapq.heappop(heap)
        
        if node == destination:
            return path
        
        if node in visited:
            continue
        visited.add(node)
        
        # Priority = 60% heuristic (direction) + 40% cost (actual distance)
        for nbr in G.neighbors(node):
            if nbr not in visited:
                edge_cost = G[node][nbr]["weight"]
                new_cost = cost_so_far + edge_cost
                h_value = heuristic(nbr, destination)
                priority = 0.6 * h_value + 0.4 * new_cost
                heapq.heappush(heap, (priority, new_cost, nbr, path + [nbr]))
    
    raise nx.NetworkXNoPath(f"No path found from {source} to {destination}")

def dfs_search(G, source, destination):
    """Improved DFS: Demerit Fix #5 - Cost-aware with pruning"""
    visited = set()
    stack = [(source, [source], 0.0)]
    best_solution = None
    best_cost = float("inf")
    
    while stack:
        node, path, cost = stack.pop()
        
        if node == destination:
            if cost < best_cost:
                best_cost = cost
                best_solution = path
            continue
        
        if node in visited:
            continue
        visited.add(node)
        
        # Explore neighbors sorted by edge weight (cheapest first)
        neighbors = sorted(
            G.neighbors(node),
            key=lambda n: G[node][n]["weight"]
        )
        
        for nbr in reversed(neighbors):
            if nbr not in visited:
                edge_cost = G[node][nbr]["weight"]
                new_cost = cost + edge_cost
                # Pruning: Skip if this path is already worse than best solution
                if new_cost < best_cost:
                    stack.append((nbr, path + [nbr], new_cost))
    
    if best_solution:
        return best_solution
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
    if algorithm == "Dijkstra (Optimal)":
        path = nx.shortest_path(G, source, destination, weight='weight')
        distance = nx.shortest_path_length(G, source, destination, weight='weight')
        return path, distance
    elif algorithm == "A* (Fast Optimal)":
        path = nx.astar_path(G, source, destination, heuristic=heuristic, weight='weight')
        distance = nx.astar_path_length(G, source, destination, heuristic=heuristic, weight='weight')
        return path, distance
    elif algorithm == "Greedy Best-First (Weight-Aware)":
        path = greedy_best_first_search(G, source, destination)
        return path, route_cost(G, path)
    elif algorithm == "AO* (Advanced)":
        path = ao_star_path(G, source, destination)
        return path, route_cost(G, path)
    raise ValueError(f"Unsupported algorithm: {algorithm}")

# 🌐 OSRM API Integration (Scalable Road Routing)
def get_osrm_route(start_coord, end_coord):
    """Get real road route from OSRM (like app1.py)"""
    try:
        start_str = f"{start_coord[1]},{start_coord[0]}"
        end_str = f"{end_coord[1]},{end_coord[0]}"
        url = f"http://router.project-osrm.org/route/v1/driving/{start_str};{end_str}?overview=full&geometries=geojson"

        response = requests.get(url, timeout=10)
        data = response.json()

        coords = data['routes'][0]['geometry']['coordinates']
        return [(lat, lon) for lon, lat in coords]

    except:
        return [start_coord, end_coord]

def get_curved_route(start_coord, end_coord, curve_strength=0.05):
    """Generate a curved path between two points (fallback when API unavailable)"""
    lat1, lon1 = start_coord
    lat2, lon2 = end_coord
    
    # Distance between points
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Create multiple points along the curve
    num_points = 50  # More points for smoother curve
    points = []
    
    for i in range(num_points + 1):
        t = i / num_points  # Progress from 0 to 1
        
        # Linear interpolation
        lat = lat1 + dlat * t
        lon = lon1 + dlon * t
        
        # Perpendicular vector (rotated 90 degrees)
        perp_lat = -dlon
        perp_lon = dlat
        
        # Normalize
        perp_length = math.sqrt(perp_lat**2 + perp_lon**2)
        if perp_length > 0:
            perp_lat /= perp_length
            perp_lon /= perp_length
        
        # Sine wave for smooth curve (maximum at midpoint)
        curve_offset = math.sin(t * math.pi) * curve_strength
        
        lat += perp_lat * curve_offset
        lon += perp_lon * curve_offset
        
        points.append((lat, lon))
    
    return points

# 🚀 Run
if st.button("🚀 Find Optimal Route"):

    if source == destination:
        st.warning("🚨 Source and Destination cannot be same!")
    else:
        try:
            G = build_weighted_graph(traffic_level, traffic_sensitivity)

            path, distance = solve_route(G, source, destination, algorithm)

            # Display results
            st.success(f"✅ Best Route Found using {algorithm}")
            
            route_display = " ➜ ".join(path)
            st.markdown(f"### 🛣️ Route: `{route_display}`")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Distance/Cost", round(distance, 2), "units")
            with col2:
                st.metric("Hops", len(path) - 1, "stops")
            with col3:
                st.metric("Traffic Mode", traffic_level, f"×{traffic_sensitivity}")

            # Debug: Show traffic impact
            st.write(f"**Traffic Settings:** Mode={traffic_level}, Sensitivity={traffic_sensitivity}")
            st.write(f"**Route Cost Calculation:** {round(distance, 2)} units")

            if show_graph:
                st.write("### 🧠 Network Details (Adjusted Weights)")
                graph_rows = []
                for u, v, d in G.edges(data=True):
                    traffic = traffic_data.get((u, v)) or traffic_data.get((v, u)) or "Low"
                    base_weight = base_G.get_edge_data(u, v, {}).get('weight', 1.0)
                    adjusted_weight = d['weight']
                    graph_rows.append({
                        "Road": f"{u} ↔ {v}",
                        "Base Weight": round(base_weight, 2),
                        "Adjusted Weight": round(adjusted_weight, 2),
                        "Traffic": traffic
                    })
                st.table(graph_rows)

            # 🗺️ Map with improved visualization (Demerit Fix #3: Curved road approximation)
            st.write("### 🗺️ Route Visualization")
            route_coords = [locations[node] for node in path]
            
            # Center map on midpoint of route
            lat_avg = sum([coord[0] for coord in route_coords]) / len(route_coords)
            lon_avg = sum([coord[1] for coord in route_coords]) / len(route_coords)
            m = folium.Map(location=[lat_avg, lon_avg], zoom_start=13)
            m.fit_bounds(route_coords)

# Draw all road connections (traffic visualization) - EXCEPT optimal path
            for u, v, d in G.edges(data=True):
                # Check if this edge is part of the optimal path
                is_on_path = False
                for i in range(len(path) - 1):
                    if (path[i] == u and path[i+1] == v) or (path[i] == v and path[i+1] == u):
                        is_on_path = True
                        break

                # Only draw non-optimal path roads with traffic colors
                if not is_on_path:
                    coords = [locations[u], locations[v]]
                    traffic = traffic_data.get((u, v)) or traffic_data.get((v, u)) or "Low"

                    # Color by traffic: Green=Low, Yellow=Medium, Red=High
                    color_map = {"Low": "green", "Medium": "orange", "High": "red"}
                    color = color_map.get(traffic, "gray")

                    # Width and dash pattern based on traffic
                    weight = 2 if traffic == "Low" else 3 if traffic == "Medium" else 4

                    folium.PolyLine(
                        coords,
                        color=color,
                        weight=weight,
                        opacity=0.6,
                        popup=f"{u} ↔ {v} ({traffic})"
                    ).add_to(m)

            # Add location markers - All locations first
            for place, coord in locations.items():
                popup_text = f"<b>{place}</b><br/>Lat: {coord[0]:.4f}<br/>Lon: {coord[1]:.4f}"
                if place in path:
                    color = "blue"
                else:
                    color = "gray"
                folium.Marker(
                    coord, 
                    popup=popup_text,
                    tooltip=place,
                    icon=folium.Icon(color=color, icon="info-sign")
                ).add_to(m)
            
            # Add SOURCE marker (green) - on top
            source_coord = locations[source]
            folium.Marker(
                source_coord,
                popup=f"<b>SOURCE: {source}</b>",
                tooltip=f"Start: {source}",
                icon=folium.Icon(color="green", icon="play", prefix="fa")
            ).add_to(m)
            
            # Add DESTINATION marker (red) - on top
            dest_coord = locations[destination]
            folium.Marker(
                dest_coord,
                popup=f"<b>DESTINATION: {destination}</b>",
                tooltip=f"End: {destination}",
                icon=folium.Icon(color="red", icon="stop", prefix="fa")
            ).add_to(m)

            # Draw route using OSRM for each segment (BLUE = OPTIMAL PATH ONLY)
            for i in range(len(path)-1):
                seg = get_osrm_route(locations[path[i]], locations[path[i+1]])
                folium.PolyLine(seg, color="blue", weight=8, opacity=0.9,
                             popup=f"🚗 OPTIMAL ROUTE: {path[i]} → {path[i+1]}").add_to(m)
            
            # Add route step markers for intermediate stops
            for i, node in enumerate(path[1:-1], 1):
                folium.Marker(
                    locations[node],
                    popup=f"Step {i+1}: {node}",
                    icon=folium.Icon(color="blue", prefix="fa", icon="circle"),
                    tooltip=f"Stop {i+1}"
                ).add_to(m)

            st.components.v1.html(m._repr_html_(), height=600)
            
            # Show route summary
            st.write("### 📊 Route Summary")
            summary_cols = st.columns(len(path))
            for i, node in enumerate(path):
                with summary_cols[i]:
                    st.write(f"**{i+1}. {node}**")
                    if i < len(path) - 1:
                        next_node = path[i+1]
                        edge_weight = G[node][next_node]["weight"]
                        traffic = traffic_data.get((node, next_node)) or traffic_data.get((next_node, node)) or "Low"
                        st.caption(f"→ {next_node} ({round(edge_weight, 2)} | {traffic})")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")