from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
from fuzzywuzzy import fuzz
import json

# Get the "stars" of the airports
def getStar(url,filename):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    data_list = []

    rows = soup.select('tr[class^="row-"]')
    print (rows)

    for row in rows:
        rank = row.find('td', class_='column-1').text
        name_container = row.find('td', class_='column-2')
        name = name_container.a.text

    # Append the data to the list
        data_list.append([name,rank])

    df = pd.DataFrame(data_list, columns=['Name', 'Rank'])
    df.to_json(filename, orient='records', force_ascii=False)


# Get other information of the airports
"""https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"""
def readairportdat(url,filename):
    data = pd.read_csv(url, header=None)
    data.columns = ['Airport ID', 'Name', 'City', 'Country', 'IATA', 'ICAO', 'Latitude', 'Longitude', 'Altitude', 'Timezone', 'DST', 'Tz database timezone', 'Type', 'Source']
    data.to_json(filename, orient='records', force_ascii=False)

def match_name(name, list_names, min_score=0):
    max_score = -1
    max_name = ""
    for name2 in list_names:
        score = fuzz.ratio(name, name2)
        if (score > min_score) & (score > max_score):
            max_name = name2
            max_score = score
    return (max_name, max_score)

# Get all the flights data

# def getFlight():
#     api = OpenSkyApi("SYZ","001213Zsy!")
#     flights = api.get_flights_from_interval(1672556400, 1672563600)
#     with open('flight.txt', 'w') as f:
#         f.write(str(flights))
# """Though I tried to use the data from OpenSky, it seems that the data is not complete, so I use the data from openflights instead."""

def readroutedat(url,filename):
    """https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"""
    data = pd.read_csv(url, header=None)
    data.columns = ['Airline', 'Airline ID', 'Source airport', 'Source airport ID', 'Destination airport', 'Destination airport ID', 'Codeshare', 'Stops', 'Equipment']
    data.to_json(filename, orient='records', force_ascii=False)


def main():
    # getStar('https://skytraxratings.com/a-z-of-airport-ratings', 'airport.json')
    # readairportdat('https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat', 'airport_info.json')
    # readroutedat('https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat', 'route_info.json')
    airport_info = pd.read_json('airport_info.json')
    airport = pd.read_json('airport.json')

    # Create a list from the 'Name' column in airport
    airport_names = airport['Name'].tolist()

    # Empty list to store matched names
    matched_names = []

    # Iterate over the Names in airport dataframe
    for name in airport_info['Name']:
        # Get the best match for each name
        match = match_name(name, airport_names, 70)
    
        # Add the matched name to the list if the score is >= 70
        if match[1]>=70:
            matched_names.append(match[0])
        else:
            matched_names.append('No Match Found')

    # Adding the matched names as a new column to the airport dataframe
    airport_info['Matched_Name'] = matched_names
    # merge the two dataframes on the 'Matched_Name' column
    merged_df = pd.merge(airport_info, airport, left_on='Matched_Name', right_on='Name', how='left')
    merged_df.to_json('airport_info_merged.json', orient='records', force_ascii=False)


def check_for_N(data):
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if isinstance(value, str) and "\\N" in value:
                return True
            if isinstance(value, dict) and check_for_N(value):
                return True
        return False
    return False

def clean_json(read_file_path, write_file_path):
    with open(read_file_path, 'r',encoding='utf-8-sig') as json_file:
        data = json.load(json_file)

    cleandata = [record for record in data if not check_for_N(record)]

    # overwrite the input file with cleaned data
    with open(write_file_path, 'w',encoding='utf-8-sig') as json_file:
        json.dump(cleandata, json_file)


if __name__ == '__main__':
    main()
    clean_json('airport_info_merged.json', 'airport_info_clean.json')
    clean_json('route_info.json', 'route_info_clean.json')
