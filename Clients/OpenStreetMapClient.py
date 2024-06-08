from typing import Union

import requests


class OpenStreetMapClient:
    """
    Client for fetching terrain data from the OpenStreetMap API.
    """
    def __init__(self, latitude: float, longitude: float):
        """
        Constructor for the OpenStreetMapClient class.
        :param latitude: Latitude of the location
        :param longitude: Longitude of the location
        """
        self.latitude = latitude
        self.longitude = longitude
        self.overpass_url = "http://overpass-api.de/api/interpreter"

    def fetch_terrain_type(self) -> Union[str, list[str]]:
        """
        Fetch terrain type from OpenStreetMap API.
        :return: A list of terrain types
        """
        overpass_query = f"""
        [out:json];
        (
          node["natural"](around:100,{self.latitude},{self.longitude});
          way["natural"](around:100,{self.latitude},{self.longitude});
          relation["natural"](around:100,{self.latitude},{self.longitude});
        );
        out body;
        """
        response = requests.get(self.overpass_url, params={'data': overpass_query})
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        elements = data.get('elements', [])

        terrain_types = set()
        for element in elements:
            if 'tags' in element and 'natural' in element['tags']:
                terrain_types.add(element['tags']['natural'])

        if not terrain_types:
            return "Unknown terrain type"
        return list(terrain_types)

    def fetch_urban_centers(self, bbox: str) -> list[dict]:
        """
        Fetch urban centers from OpenStreetMap API.
        :param bbox: String representing bounding box coordinates for the region
        :return: A list of dictionaries containing the name, latitude, and longitude of urban centers inside the region
        """
        overpass_query = f"""
        [out:json];
        (
          node["place"="city"]({bbox});
          node["place"="town"]({bbox});
        );
        out body;
        """
        response = requests.get(self.overpass_url, params={'data': overpass_query})
        response.raise_for_status()
        data = response.json()
        centers = [{'name': element['tags']['name'], 'latitude': element['lat'], 'longitude': element['lon']}
                   for element in data['elements'] if 'tags' in element and 'name' in element['tags']]
        return centers

