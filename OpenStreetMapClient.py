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

