import streamlit as st
import networkx as nx
import folium
import copy

st.set_page_config(page_title="Route Optimizer", layout="centered")
st.title("🚦 Smart Traffic Route Optimization (Nagpur)")

# Locations
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

# Base graph
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

# Traffic data
traffic_data = {
    ("Sitabuldi","Dharampeth"): "High",
    ("Sitabuldi","Ramdaspeth"): "Low",
    ("Dharampeth","Ramdaspeth"): "Medium",
    ("Dharampeth","Medical Square"): "High",
    ("Ramdaspeth","Manish Nagar"): "Low",
    ("Medical Square","Manish Nagar"): "Medium",
    ("Trimurti Nagar","Dharampeth"): "Low",
    ("Manish Nagar","Airport"): "Medium",
    ("Ramdaspeth","Wardha Road"): "High",
    ("Wardha Road","Airport"): "Low"
}

nodes = list(locations.keys())

# UI
source = st.selectbox("📍 Select Source", nodes)
destination = st.selectbox("🏁 Select Destination", nodes)
traffic_level = st.selectbox("🚦 Traffic Mode", ["Low", "Medium", "High"])

# Mode factor
def get_mode_factor(mode):
    if mode == "Low":
        return 0
    elif mode == "Medium":
        return 2
    else:
        return 5

if st.button("🚀 Find Optimal Route"):

    if source == destination:
        st.warning("Source and Destination cannot be same!")
    else:
        try:
            G = copy.deepcopy(base_G)

            # APPLY NEW TRAFFIC LOGIC 🔥
            for u, v, d in G.edges(data=True):

                base_weight = d['weight']
                traffic = traffic_data.get((u, v)) or traffic_data.get((v, u)) or "Low"

                # traffic penalty
                if traffic == "Low":
                    traffic_penalty = 0
                elif traffic == "Medium":
                    traffic_penalty = 3
                else:
                    traffic_penalty = 8

                mode_factor = get_mode_factor(traffic_level)

                # FINAL WEIGHT (IMPORTANT)
                d['weight'] = base_weight + (traffic_penalty * mode_factor)

            # Shortest path
            path = nx.shortest_path(G, source, destination, weight='weight')
            distance = nx.shortest_path_length(G, source, destination, weight='weight')

            st.success(f"✅ Best Route: {' → '.join(path)}")
            st.info(f"📏 Estimated Distance: {round(distance,2)}")

            # Alternative path
            all_paths = list(nx.all_simple_paths(G, source, destination))
            all_paths_sorted = sorted(
                all_paths,
                key=lambda p: sum(G[p[i]][p[i+1]]['weight'] for i in range(len(p)-1))
            )

            if len(all_paths_sorted) > 1:
                st.write(f"🔁 Alternative Route: {' → '.join(all_paths_sorted[1])}")

            # Map
            route_coords = [locations[node] for node in path]

            m = folium.Map(location=[21.1458, 79.0882], zoom_start=12)
            m.fit_bounds(route_coords)

            # Markers
            for place, coord in locations.items():
                if place in path:
                    color = "green" if place == source else "red" if place == destination else "blue"
                    folium.Marker(coord, popup=place, icon=folium.Icon(color=color)).add_to(m)
                else:
                    folium.CircleMarker(location=coord, radius=5, color="gray", fill=True, fill_opacity=0.3).add_to(m)

            # Roads color
            for u, v, d in G.edges(data=True):
                coords = [locations[u], locations[v]]
                traffic = traffic_data.get((u, v)) or traffic_data.get((v, u)) or "Low"

                if traffic == "Low":
                    color = "green"
                elif traffic == "Medium":
                    color = "orange"
                else:
                    color = "red"

                folium.PolyLine(coords, color=color, weight=3, opacity=0.6).add_to(m)

            # Best route highlight
            folium.PolyLine(route_coords, color="blue", weight=6).add_to(m)

            # Show map
            st.components.v1.html(m._repr_html_(), height=600)

        except Exception as e:
            st.error(f"Error: {e}")