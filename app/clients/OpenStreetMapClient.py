from functools import lru_cache
from math import pi, cos
from typing import Union, Any
import geopy.distance

import requests
import logging


class OpenStreetMapClient:
    _logger = logging.getLogger(__name__)
    """
    Client for fetching terrain data from the OpenStreetMap API.
    """
    def __init__(self, latitude: float, longitude: float):
        """
        Constructor for the OpenStreetMapClient class.
        :param latitude: Latitude of the location
        :param longitude: Longitude of the location
        """
        self.logger = OpenStreetMapClient._logger
        self.latitude = latitude
        self.longitude = longitude
        self.overpass_url = "https://overpass-api.de/api/interpreter"

    @classmethod
    @lru_cache(maxsize=1024)
    def fetch_terrain_type(cls, latitude: float, longitude: float) -> Union[str, list[Any]]:
        """Class-level cache for terrain types"""
        cls._logger.info(f"Fetching terrain for {latitude},{longitude}")
        url = "https://overpass-api.de/api/interpreter"
        query = f"""
            [out:json];
            (
              node["natural"](around:100,{latitude},{longitude});
              way["natural"](around:100,{latitude},{longitude});
              relation["natural"](around:100,{latitude},{longitude});
            );
            out body;
        """
        try:
            cls._logger.info("Fetching terrain type...")
            response = requests.get(url, params={'data': query})
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()
            elements = data.get('elements', [])

            terrain_types = set()
            for element in elements:
                if 'tags' in element and 'natural' in element['tags']:
                    terrain_types.add(element['tags']['natural'])

            if not terrain_types:
                cls._logger.info("No terrain type found.")
                return "Unknown terrain type"
            cls._logger.info("Terrain type fetched successfully.")
            return list(terrain_types)
        except requests.exceptions.RequestException as e:
            cls._logger.error(f"Terrain fetch failed: {e}")
            return "Unknown"

    def fetch_urban_centers(self, radius_km: int = 40) -> list[dict[str, Union[str, float]]]:
        """
        Fetch urban centers from OpenStreetMap API.
        :param radius_km: Radius in kilometers for the bounding box
        :return: A list of dictionaries containing the name, latitude, and longitude of urban centers inside the region
        """
        def calculate_bounding_box(lat: float, lon: float, radius: int) -> str:
            lat_per_km = 1 / 111.0  # Approximate kilometers per degree of latitude
            lon_per_km = 1 / (111.0 * abs(cos(lat * (pi / 180.0))))  # Approximate kilometers per degree of longitude

            lat_offset = lat_per_km * radius
            lon_offset = lon_per_km * radius

            south = lat - lat_offset
            north = lat + lat_offset
            west = lon - lon_offset
            east = lon + lon_offset

            return f"{south},{west},{north},{east}"

        bbox = calculate_bounding_box(self.latitude, self.longitude, radius_km)
        self.logger.info(f"Bounding box for radius {radius_km} km: {bbox}")

        overpass_query = f"""
        [out:json];
        (
          node["place"="city"]({bbox});
          node["place"="town"]({bbox});
        );
        out body;
        """
        try:
            self.logger.info("Fetching urban centers...")
            response = requests.get(self.overpass_url, params={'data': overpass_query})
            response.raise_for_status()
            data = response.json()
            centers = [{'name': element['tags']['name'], 'latitude': element['lat'], 'longitude': element['lon'], 'distance': geopy.distance.distance((self.latitude, self.longitude), (element['lat'], element['lon'])).kilometers}
                       for element in data['elements'] if 'tags' in element and 'name' in element['tags']]
            centers.sort(key=lambda x: x['distance'])
            self.logger.info("Urban centers fetched successfully.")
            return centers
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching urban centers: {e}")
            return []
