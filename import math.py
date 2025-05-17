import math
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)*2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)*2
    return 2 * R * math.asin(math.sqrt(a))

def compute_distance_matrix(cities):
    n = len(cities)
    dist = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                dist[i][j] = haversine(
                    cities[i]['lat'], cities[i]['lon'],
                    cities[j]['lat'], cities[j]['lon']
                )
    return dist

def greedy_tsp(dist):
    n = len(dist)
    visited = [False]*n
    path = [0]
    visited[0] = True
    for _ in range(n-1):
        last = path[-1]
        next_city = min((dist[last][j], j) for j in range(n) if not visited[j])[1]
        path.append(next_city)
        visited[next_city] = True
    return path

def two_opt(path, dist):
    n = len(path)
    improved = True
    while improved:
        improved = False
        for i in range(1, n-2):
            for j in range(i+1, n):
                if j-i == 1: continue
                new_path = path[:i] + path[i:j][::-1] + path[j:]
                if tour_length(new_path, dist) < tour_length(path, dist):
                    path = new_path
                    improved = True
    return path

def tour_length(path, dist):
    return sum(dist[path[i]][path[(i+1)%len(path)]] for i in range(len(path)))

import csv
import json
from tsp_solver.greedy import two_opt, tour_length
def read_cities(filename):
    cities = []
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cities.append({'name': row['Name'], 'lat': float(row['Lat']), 'lon': float(row['Lon'])})
    return cities

def to_geojson(cities, path):
    features = []
    for i in range(len(path)):
        c = cities[path[i]]
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [c['lon'], c['lat']]},
            "properties": {"name": c['name'], "order": i+1}
        })
    return {
        "type": "FeatureCollection",
        "features": features
    }

def main():
    cities = read_cities('cities.csv')
    dist = compute_distance_matrix(cities)
    path = greedy_tsp(dist)
    path = two_opt(path, dist)
    print("Optimal tour (returns to start):")
    for i, idx in enumerate(path):
        print(f"{i+1}) {cities[idx]['name']}")
    print(f"Total distance: {tour_length(path, dist):.2f} km")
    geojson = to_geojson(cities, path)
    with open('route.geojson', 'w') as f:
        json.dump(geojson, f)
    print("Route written to route.geojson.")

if __name__ == "_main_":
    main()