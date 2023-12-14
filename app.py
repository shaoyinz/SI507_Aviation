from flask import Flask, render_template, request
from create_map import create_map,create_map_path
import json
from collections import deque

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_airport', methods=['POST'])
def search_airport():
    country = request.form.get('country')
    city = request.form.get('city')
    with open('graph.json') as f:
        data = json.load(f)
    results = {k: v for k, v in data.items() if v['country'].lower() == country.lower() and v['city'].lower() == city.lower()}
    return render_template('airports.html', airports=results)

@app.route('/search_airport_by_location', methods=['POST'])
def search_airport_by_location():
    min_lat = float(request.form.get('min_lat'))
    max_lat = float(request.form.get('max_lat'))
    min_lon = float(request.form.get('min_lon'))
    max_lon = float(request.form.get('max_lon'))
    with open('graph.json') as f:
        data = json.load(f)
    results = {k: v for k, v in data.items() if min_lat <= v['latitude'] <= max_lat and min_lon <= v['longitude'] <= max_lon}
    return render_template('airports.html', airports=results)

@app.route('/search_flights', methods=['POST'])
def search_flights():
    airline = request.form.get('airline').lower()  # save the user's choice in a variable
    with open('graph.json') as f:
        data = json.load(f)

    # Filter the routes where the 'Airline' field match the airline input by the user.
    results = {}
    for airport in data.values():
        for dest, route in airport['departing_routes'].items():
            if route['Airline'].lower() == airline:
                # Add the route to the results: dictionary keys are source-destination airport pairs.
                route_key = f"{airport['iata']}-{route['Destination']}"
                results[route_key] = route

    routes=[]
    for k, v in results.items():
        source, destination = k.split("-")
        for key, value in data.items():
            if value['iata'] == source:
                source_airport = value
            if value['iata'] == destination:
                destination_airport = value
        route = {'source': source_airport, 'destination': destination_airport, 'details': v}
        routes.append(route)
    map_html = create_map(routes)
    return render_template('flights.html', flights=routes, map_html=map_html)

def shortest_path(graph, start_id, end_id):
    visited = {}
    queue = deque([[(start_id, None, None, None)]])
    while queue:
        path = queue.popleft()
        node = path[-1][0]
        if node not in visited:
            if node in graph:
                neighbours = graph[node]["departing_routes"].items()
                for neighbour, details in neighbours:
                    if neighbour in graph:
                        new_path = list(path)
                        new_path.append((neighbour, details["Destination"],
                                         details["Airline"], details["Equipment"]))
                        queue.append(new_path)
                        if neighbour == end_id:
                            return new_path
            visited[node] = True
    return "Route not available"


@app.route('/calculate_path', methods=['POST'])
def calculate_path():
    source = request.form.get('source')
    destination = request.form.get('destination')
    with open('graph.json') as f:
        data = json.load(f)
    path = shortest_path(data, source, destination) 
    path_airports = [data[id] for id, _, _, _ in path] if path != "Route not available" else []
    path_details = [{'id': id, 
                     'Destination': dest, 
                     'Airline': airline, 
                     'Equipment': equip
                    } for id, dest, airline, equip in path] if path != "Route not available" else []
    # generate map
    map_html = create_map_path(path_airports) if path_airports else ""
    return render_template('path.html', path=path_airports, path_details=path_details, map_html=map_html)

if __name__ == '__main__':
    app.run(debug=True)