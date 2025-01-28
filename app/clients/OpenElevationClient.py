from pathlib import Path
from typing import Union

import requests
import requests_cache
import logging
import os


class OpenElevationClient:
    """
    Client for fetching elevation data from the Open-Elevation API.
    """
    def __init__(self, latitude: float, longitude: float, cache_expiry: int = 3600):
        """
        Constructor for the OpenElevationClient class.
        :param latitude: Latitude of the location
        :param longitude: Longitude of the location
        """
        self.logger = logging.getLogger(__name__)
        self.latitude = latitude
        self.longitude = longitude
        self.elevation_url = "https://api.open-elevation.com/api/v1/lookup"
        self.logger.info(f"Initialized OpenElevationClient for coordinates ({latitude}, {longitude})")
        CACHE_DIR = Path(os.getcwd()) / "cache"  # Creates cache in the project's root
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.session = requests_cache.CachedSession(str(CACHE_DIR / "elevation.db"), expire_after=cache_expiry)

        self.logger.info(f"Initialized requests_cache for OpenElevationClient.")

    def fetch_elevation(self) -> Union[float, None]:
        """
        Fetch elevation data from the Open-Elevation API.
        :return: Elevation in meters
        """
        try:
            self.logger.info("Fetching elevation data...")
            payload = {"locations": [{"latitude": self.latitude, "longitude": self.longitude}]}
            response = requests.post(self.elevation_url, json=payload)
            response.raise_for_status()
            data = response.json()
            elevation = data['results'][0]['elevation']
            self.logger.info("Elevation data fetched successfully.")
            return elevation
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching elevation data: {e}")
            return None
