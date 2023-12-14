import folium
from folium.plugins import AntPath

def create_map(routes):
    # create a new folium map centered on World
    flight_map = folium.Map(location=[0, 0], zoom_start=2)

    for route in routes:
        source_airport = route['source']
        destination_airport = route['destination']

        # add source and destination markers
        folium.Marker((source_airport['latitude'], source_airport['longitude']), popup=source_airport['name']).add_to(flight_map)
        folium.Marker((destination_airport['latitude'], destination_airport['longitude']), popup=destination_airport['name']).add_to(flight_map)

        # add line between source and destination
        folium.PolyLine(
            locations=[(source_airport['latitude'], source_airport['longitude']), 
                       (destination_airport['latitude'], destination_airport['longitude'])], 
            color='blue'
        ).add_to(flight_map)

    # return the map's html
    return flight_map._repr_html_()

def create_map_path(path_airports):
    # create a new folium map centered on World
    flight_map = folium.Map(location=[0, 0], zoom_start=2)

    for index in range(len(path_airports) - 1):
        source_airport = path_airports[index]
        destination_airport = path_airports[index + 1]

        # add source and destination markers
        folium.Marker((source_airport['latitude'], source_airport['longitude']), popup=source_airport['name']).add_to(flight_map)
        folium.Marker((destination_airport['latitude'], destination_airport['longitude']), popup=destination_airport['name']).add_to(flight_map)

        # add line between source and destination
        AntPath(
            locations=[(source_airport['latitude'], source_airport['longitude']), 
                       (destination_airport['latitude'], destination_airport['longitude'])], 
            color='blue'
        ).add_to(flight_map)

    # return the map's html
    return flight_map._repr_html_()