🚦 Smart Traffic Route Optimization (Nagpur)
📌 Project Overview

This project is an interactive traffic route optimization system built using Python and Streamlit. It helps users find the most efficient path between two locations in Nagpur by considering dynamic traffic conditions, graph-based algorithms, and real-time simulation.

The system visualizes routes on a map and allows users to experiment with different algorithms and traffic scenarios.

🎯 Features
📍 Multiple Location Support (Predefined + Custom GPS locations)
🚦 Real-time Traffic Simulation
🧠 Multiple Pathfinding Algorithms
🌡️ Traffic Sensitivity Adjustment
🗺️ Interactive Map Visualization (Folium)
➕ Custom Location Addition with Coordinates
💾 Persistent Storage using JSON
🔄 Dynamic Graph Weight Adjustment

🧠 Algorithms Implemented
Dijkstra Algorithm (Optimal)
A* Algorithm (Fast Optimal)
Greedy Best-First Search (Heuristic-based)
AO* Algorithm (Advanced Pathfinding)

⚙️ Tech Stack
Frontend/UI: Streamlit
Graph Processing: NetworkX
Map Visualization: Folium
Data Handling: JSON, Python
API Integration: OSRM (Open Source Routing Machine)

📂 Project Structure

├── app.py
├── custom_locations.json
├── README.md

🚀 How to Run the Project
1. Install Dependencies

pip install streamlit networkx folium requests

2. Run the Application

streamlit run app.py

3. Open in Browser

http://localhost:8501

🧪 How It Works
Select Source and Destination
Choose Traffic Mode (Low / Medium / High)
Select Algorithm
System builds a weighted graph and calculates the optimal route
Result is displayed with map visualization
📊 Traffic Modeling

Traffic levels affect route cost:

Low Traffic → Minimal delay
Medium Traffic → Moderate delay
High Traffic → Maximum delay

Formula used:
Adjusted Weight = Base Weight + (Penalty × Traffic Factor × Sensitivity)

🗺️ Map Visualization
🔵 Blue Line → Optimal Route
🟢 Green → Low Traffic
🟠 Orange → Medium Traffic
🔴 Red → High Traffic
📍 Markers for source, destination, and stops
📌 Key Functionalities
Custom GPS-based location addition
Real-time traffic updates
Heuristic-based optimization
Graph-based routing
Interactive dashboard

📈 Advantages
User-friendly interface
Real-time simulation
Multiple algorithm comparison
Scalable design
Useful for smart city applications

⚠️ Limitations
Traffic is simulated (not real-time data)
Limited to predefined locations
Requires internet for OSRM API

🔮 Future Scope
Integration with live traffic APIs
AI-based traffic prediction
Mobile application
Real-time GPS tracking
Expansion to other cities

👨‍💻 Author
Shantanu Deshmukh
